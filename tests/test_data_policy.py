import csv
import io
import sqlite3

import pytest
from fastapi.testclient import TestClient

from datatrust_api.main import create_app
from datatrust_api.profiles import get_profile
from datatrust_api.validator import InvalidDataset, validate_orders_csv


HEADERS = ("order_id", "customer_id", "email", "amount", "currency", "order_date")


def csv_payload(row, headers=HEADERS):
    stream = io.StringIO(newline="")
    writer = csv.writer(stream, lineterminator="\n")
    writer.writerow(headers)
    writer.writerow(row)
    return stream.getvalue().encode("utf-8")


def valid_row(**overrides):
    values = {
        "order_id": "O1",
        "customer_id": "C1",
        "email": "user@example.invalid",
        "amount": "19.99",
        "currency": "USD",
        "order_date": "2026-10-26",
    }
    values.update(overrides)
    return [values[field] for field in HEADERS]


@pytest.mark.parametrize(
    "amount",
    ["+1.00", "-1.00", "1e2", "1,00", "1.", ".50", "1.234", "1000000000000.00"],
)
def test_amount_policy_rejects_signs_exponent_separators_scale_and_range(amount):
    _, valid, issues = validate_orders_csv(csv_payload(valid_row(amount=amount)))

    assert valid == 0
    assert any(issue["code"] == "INVALID_AMOUNT" for issue in issues)


@pytest.mark.parametrize(
    "amount",
    ["0.01", "1", "0001.20", "999999999999.99"],
)
def test_amount_policy_accepts_documented_boundaries_without_rounding(amount):
    assert validate_orders_csv(csv_payload(valid_row(amount=amount))) == (1, 1, [])


def test_profile_exposes_explicit_decimal_policy_by_currency():
    profile = get_profile("orders_v1")
    policy = profile.decimal_policies["amount"]

    assert str(policy.minimum) == "0.01"
    assert str(policy.maximum) == "999999999999.99"
    assert policy.currency_field == "currency"
    assert dict(policy.max_decimal_places_by_currency) == {
        "CRC": 2,
        "EUR": 2,
        "USD": 2,
    }
    assert policy.allow_scientific is False


def test_character_and_utf8_byte_boundaries_are_enforced_for_identifier():
    exact_characters = "A" * 128
    too_many_characters = "A" * 129
    exact_bytes = "😀" * 64
    too_many_bytes = "😀" * 65

    for accepted in (exact_characters, exact_bytes):
        assert validate_orders_csv(csv_payload(valid_row(order_id=accepted))) == (
            1,
            1,
            [],
        )

    for rejected in (too_many_characters, too_many_bytes):
        _, valid, issues = validate_orders_csv(
            csv_payload(valid_row(order_id=rejected))
        )
        assert valid == 0
        assert any(issue["code"] == "VALUE_TOO_LONG" for issue in issues)
        assert all(rejected not in issue["message"] for issue in issues)


def test_invisible_control_or_format_characters_are_invalid_in_identifiers():
    for identifier in ("ABC\x00DEF", "ABC\u200bDEF"):
        _, valid, issues = validate_orders_csv(
            csv_payload(valid_row(order_id=identifier))
        )
        assert valid == 0
        assert any(issue["code"] == "INVALID_IDENTIFIER" for issue in issues)


def test_header_limits_and_invisible_characters_are_structural_errors():
    with pytest.raises(InvalidDataset, match="64 caracteres"):
        validate_orders_csv(csv_payload(valid_row(), headers=("x" * 65, *HEADERS[1:])))

    with pytest.raises(InvalidDataset, match="control o formato"):
        validate_orders_csv(
            csv_payload(valid_row(), headers=("order\u200b_id", *HEADERS[1:]))
        )


def test_large_csv_field_reaches_explicit_policy_instead_of_implicit_parser_limit():
    headers = (*HEADERS, "extra_note")
    payload = csv_payload([*valid_row(), "x" * 140_000], headers=headers)

    total, valid, issues = validate_orders_csv(payload)

    assert (total, valid) == (1, 0)
    assert any(
        issue["field_name"] == "_extra" and issue["code"] == "VALUE_TOO_LONG"
        for issue in issues
    )


def test_api_does_not_echo_or_persist_overlong_sensitive_value(tmp_path):
    db_path = tmp_path / "limits.db"
    marker = "PRIVATE_LIMIT_MARKER_7D31"
    private_value = marker + ("X" * 200)

    with TestClient(create_app(str(db_path))) as client:
        response = client.post(
            "/api/v1/runs",
            files={
                "file": (
                    "neutral.csv",
                    csv_payload(valid_row(order_id=private_value)),
                    "text/csv",
                )
            },
        )
        run_id = response.json()["id"]
        combined = response.text + client.get(f"/api/v1/runs/{run_id}").text

    with sqlite3.connect(db_path) as db:
        database_dump = "\n".join(db.iterdump())

    assert response.status_code == 201
    assert response.json()["valid_rows"] == 0
    assert response.json()["issue_count"] == 1
    assert marker not in combined
    assert marker not in database_dump
