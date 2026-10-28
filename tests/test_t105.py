import csv
import io
import sqlite3

import pytest
from fastapi.testclient import TestClient

from datatrust_api.main import MAX_FILE_BYTES, MAX_SQLITE_OFFSET, create_app
from datatrust_api.validator import InvalidDataset, MAX_ROWS, validate_orders_csv


HEADERS = ("order_id", "customer_id", "email", "amount", "currency", "order_date")


def csv_payload(rows, headers=HEADERS, *, bom=False):
    stream = io.StringIO(newline="")
    writer = csv.writer(stream, lineterminator="\n")
    writer.writerow(headers)
    writer.writerows(rows)
    encoded = stream.getvalue().encode("utf-8")
    return (b"\xef\xbb\xbf" + encoded) if bom else encoded


def valid_row(number=1, **overrides):
    values = {
        "order_id": f"O{number}",
        "customer_id": f"C{number}",
        "email": f"user{number}@example.invalid",
        "amount": "19.99",
        "currency": "CRC",
        "order_date": "2026-10-25",
    }
    values.update(overrides)
    return [values[field] for field in HEADERS]


def rows_payload(count):
    header = ",".join(HEADERS).encode() + b"\n"
    rows = (
        f"O{i},C{i},u{i}@example.invalid,1,USD,2026-10-25\n".encode()
        for i in range(count)
    )
    return header + b"".join(rows)


def exact_size_payload():
    """Genera 10.000 filas válidas sin depender de archivos temporales."""
    header = ",".join((*HEADERS, "padding")).encode() + b"\n"
    prefixes = [
        f"O{i},C{i},u{i}@example.invalid,1,USD,2026-10-25,".encode()
        for i in range(MAX_ROWS)
    ]
    minimum_size = len(header) + sum(len(prefix) + 1 for prefix in prefixes)
    padding_size = MAX_FILE_BYTES - minimum_size
    assert padding_size >= 0
    common, extra = divmod(padding_size, MAX_ROWS)
    payload = header + b"".join(
        prefix + (b"x" * (common + (index < extra))) + b"\n"
        for index, prefix in enumerate(prefixes)
    )
    assert len(payload) == MAX_FILE_BYTES
    return payload


@pytest.fixture(scope="module")
def csv_at_size_limit():
    return exact_size_payload()


def test_file_size_limit_accepts_exactly_two_mib_and_rejects_one_extra_byte(
    tmp_path, csv_at_size_limit
):
    with TestClient(create_app(str(tmp_path / "runs.db"))) as client:
        accepted = client.post(
            "/api/v1/runs",
            files={"file": ("limit.csv", csv_at_size_limit, "text/csv")},
        )
        rejected = client.post(
            "/api/v1/runs",
            files={"file": ("over-limit.csv", csv_at_size_limit + b"x", "text/csv")},
        )

        assert accepted.status_code == 201, accepted.text
        assert accepted.json()["total_rows"] == MAX_ROWS
        assert accepted.json()["valid_rows"] == MAX_ROWS
        assert rejected.status_code == 413, rejected.text
        assert len(client.get("/api/v1/runs?limit=100").json()) == 1


def test_multipart_overhead_is_not_counted_as_csv_file_size(tmp_path, csv_at_size_limit):
    with TestClient(create_app(str(tmp_path / "runs.db"))) as client:
        request = client.build_request(
            "POST",
            "/api/v1/runs",
            files={"file": ("limit.csv", csv_at_size_limit, "text/csv")},
        )
        assert len(csv_at_size_limit) == MAX_FILE_BYTES
        assert int(request.headers["content-length"]) > MAX_FILE_BYTES

        response = client.send(request)

    assert response.status_code == 201, response.text


@pytest.mark.parametrize(
    ("row_count", "expected_status"),
    [(MAX_ROWS, 201), (MAX_ROWS + 1, 422)],
)
def test_data_row_limit_is_exact_and_does_not_partially_persist(
    tmp_path, row_count, expected_status
):
    payload = rows_payload(row_count)
    assert len(payload) < MAX_FILE_BYTES

    with TestClient(create_app(str(tmp_path / f"rows-{row_count}.db"))) as client:
        response = client.post(
            "/api/v1/runs",
            files={"file": ("rows.csv", payload, "text/csv")},
        )
        runs = client.get("/api/v1/runs").json()

    assert response.status_code == expected_status, response.text
    assert len(runs) == (1 if expected_status == 201 else 0)
    if expected_status == 201:
        assert response.json()["total_rows"] == MAX_ROWS
        assert response.json()["valid_rows"] == MAX_ROWS


def test_utf8_bom_and_valid_unicode_are_accepted_but_bad_encoding_is_rejected(tmp_path):
    unicode_row = valid_row(
        order_id="Pedido-Café-東京",
        customer_id="Cliente-Ñandú",
        email="zoë@example.invalid",
    )
    bad_encoding = csv_payload([valid_row(email="josé@example.invalid")]).decode(
        "utf-8"
    ).encode("cp1252")

    with TestClient(create_app(str(tmp_path / "encoding.db"))) as client:
        accepted = client.post(
            "/api/v1/runs",
            files={"file": ("unicode.csv", csv_payload([unicode_row], bom=True), "text/csv")},
        )
        rejected = client.post(
            "/api/v1/runs",
            files={"file": ("cp1252.csv", bad_encoding, "text/csv")},
        )

    assert accepted.status_code == 201, accepted.text
    assert accepted.json()["valid_rows"] == 1
    assert rejected.status_code == 422, rejected.text
    assert "UTF-8" in rejected.json()["detail"]


def test_canonically_equivalent_unicode_order_ids_are_duplicates():
    payload = csv_payload(
        [valid_row(1, order_id="Café"), valid_row(2, order_id="Cafe\u0301")]
    )

    total, valid, issues = validate_orders_csv(payload)

    assert (total, valid) == (2, 1)
    assert [issue["code"] for issue in issues] == ["DUPLICATE"]


def test_schema_allows_extra_columns_and_rejects_duplicate_or_missing_required_names(tmp_path):
    extra_headers = (*HEADERS, "source_note")
    extra_payload = csv_payload(
        [(*valid_row(), "entrada externa, lote α")], headers=extra_headers
    )
    duplicate_headers = (*HEADERS, "order_id")
    duplicate_payload = csv_payload(
        [(*valid_row(), "otro-id")], headers=duplicate_headers
    )
    replacement_headers = (*HEADERS[:-1], "unexpected_date")
    replacement_payload = csv_payload([valid_row()], headers=replacement_headers)

    with TestClient(create_app(str(tmp_path / "schema.db"))) as client:
        extra = client.post(
            "/api/v1/runs", files={"file": ("extra.csv", extra_payload, "text/csv")}
        )
        duplicate = client.post(
            "/api/v1/runs",
            files={"file": ("duplicate.csv", duplicate_payload, "text/csv")},
        )
        replacement = client.post(
            "/api/v1/runs",
            files={"file": ("unexpected.csv", replacement_payload, "text/csv")},
        )

    assert extra.status_code == 201, extra.text
    assert extra.json()["valid_rows"] == 1
    assert extra.json()["issue_count"] == 0
    assert duplicate.status_code == 422, duplicate.text
    assert replacement.status_code == 422, replacement.text
    assert "order_date" in replacement.json()["detail"]


@pytest.mark.parametrize("amount", ["NaN", "sNaN", "Infinity", "-Infinity", "0", "-0.01"])
def test_non_finite_or_non_positive_amounts_are_rejected(amount):
    _, valid, issues = validate_orders_csv(csv_payload([valid_row(amount=amount)]))

    assert valid == 0
    assert any(issue["code"] == "INVALID_AMOUNT" for issue in issues)


@pytest.mark.parametrize("amount", ["9" * 1_000 + ".99", "0." + "0" * 1_000 + "1"])
def test_extreme_finite_amounts_are_rejected_by_explicit_length_policy(amount):
    total, valid, issues = validate_orders_csv(csv_payload([valid_row(amount=amount)]))

    assert (total, valid) == (1, 0)
    assert [issue["code"] for issue in issues] == ["VALUE_TOO_LONG"]
    assert amount not in issues[0]["message"]


@pytest.mark.parametrize("order_date", ["0000-01-01", "2025-02-29", "2026-13-01"])
def test_calendar_invalid_dates_are_rejected(order_date):
    _, valid, issues = validate_orders_csv(
        csv_payload([valid_row(order_date=order_date)])
    )

    assert valid == 0
    assert any(issue["code"] == "INVALID_DATE" for issue in issues)


def test_malformed_csv_and_control_character_in_email_are_rejected():
    malformed = csv_payload([]) + b'"unclosed,C1,a@example.invalid,1,USD,2026-10-25'
    with pytest.raises(InvalidDataset, match="CSV mal formado"):
        validate_orders_csv(malformed)

    _, valid, issues = validate_orders_csv(
        csv_payload([valid_row(email="ana\x00@example.invalid")])
    )
    assert valid == 0
    assert any(issue["code"] == "INVALID_EMAIL" for issue in issues)


def test_real_pagination_covers_middle_last_and_boundary_pages(tmp_path):
    with TestClient(create_app(str(tmp_path / "pagination.db"))) as client:
        for number in range(5):
            response = client.post(
                "/api/v1/runs",
                files={
                    "file": (
                        f"orders-{number}.csv",
                        csv_payload([valid_row(number)]),
                        "text/csv",
                    )
                },
            )
            assert response.status_code == 201, response.text

        all_runs = client.get("/api/v1/runs?limit=100&offset=0").json()
        assert len(all_runs) == 5
        assert client.get("/api/v1/runs?limit=2&offset=1").json() == all_runs[1:3]
        assert client.get("/api/v1/runs?limit=2&offset=4").json() == all_runs[4:]
        assert client.get("/api/v1/runs?limit=2&offset=5").json() == []
        assert len(client.get("/api/v1/runs?limit=1").json()) == 1
        assert client.get(
            f"/api/v1/runs?limit=100&offset={MAX_SQLITE_OFFSET}"
        ).json() == []

        invalid = client.post(
            "/api/v1/runs",
            files={"file": ("invalid.csv", csv_payload([["", "", "", "", "", ""]]), "text/csv")},
        )
        assert invalid.status_code == 201, invalid.text
        run_id = invalid.json()["id"]
        all_issues = client.get(f"/api/v1/runs/{run_id}/issues?limit=500").json()
        assert len(all_issues) == 6
        assert client.get(
            f"/api/v1/runs/{run_id}/issues?limit=2&offset=2"
        ).json() == all_issues[2:4]
        assert client.get(
            f"/api/v1/runs/{run_id}/issues?limit=2&offset=4"
        ).json() == all_issues[4:]
        assert client.get(
            f"/api/v1/runs/{run_id}/issues?limit=2&offset=6"
        ).json() == []
        assert len(client.get(f"/api/v1/runs/{run_id}/issues?limit=1").json()) == 1
        assert client.get(
            f"/api/v1/runs/{run_id}/issues?offset={MAX_SQLITE_OFFSET}"
        ).json() == []


def test_formula_prefixes_and_sensitive_row_data_are_not_stored_or_exposed(tmp_path):
    db_path = tmp_path / "privacy.db"
    sensitive_filename = "student-12345+private@example.invalid.csv"
    raw_marker = "T105_PRIVATE_ROW_7E4F"
    formulas = ["=1+1", "+SUM(A1:A2)", "-2+3", "@SUM(A1:A2)"]
    rows = [
        valid_row(
            index,
            order_id=formula,
            customer_id=f"{raw_marker}_{index}",
            email=f"{raw_marker.lower()}.{index}@example.invalid",
        )
        for index, formula in enumerate(formulas, start=1)
    ]

    with TestClient(create_app(str(db_path))) as client:
        created = client.post(
            "/api/v1/runs",
            files={"file": (sensitive_filename, csv_payload(rows), "text/csv")},
        )
        assert created.status_code == 201, created.text
        assert created.json()["total_rows"] == len(formulas)
        assert created.json()["valid_rows"] == len(formulas)
        assert created.json()["issue_count"] == 0
        run_id = created.json()["id"]
        response_text = "\n".join(
            [
                created.text,
                client.get("/api/v1/runs?limit=100").text,
                client.get(f"/api/v1/runs/{run_id}").text,
                client.get(f"/api/v1/runs/{run_id}/issues").text,
            ]
        )

    with sqlite3.connect(db_path) as db:
        database_dump = "\n".join(db.iterdump())

    for secret in [sensitive_filename, raw_marker, raw_marker.lower(), *formulas]:
        assert secret not in response_text
        assert secret not in database_dump
