import csv
import io

from fastapi.testclient import TestClient

from datatrust_api import store
from datatrust_api.main import create_app


def sample_run(run_id, issue_count):
    return {
        "id": run_id,
        "filename": f"{run_id}.csv",
        "profile": "orders_v1",
        "status": "completed",
        "total_rows": issue_count,
        "valid_rows": 0,
        "invalid_rows": issue_count,
        "issue_count": issue_count,
        "created_at": "2026-10-25T00:00:00+00:00",
    }


def parse_csv_response(response):
    text = response.content.decode("utf-8-sig")
    return list(csv.DictReader(io.StringIO(text, newline="")))


def test_export_streams_every_issue_beyond_detail_limit(tmp_path):
    db_path = str(tmp_path / "export.db")
    run_id = "11111111-1111-4111-8111-111111111111"
    issues = [
        {
            "row_number": number + 2,
            "field_name": "email",
            "code": "INVALID_EMAIL",
            "message": "Formato de correo no reconocido.",
        }
        for number in range(105)
    ]

    with TestClient(create_app(db_path)) as client:
        store.save_run(db_path, sample_run(run_id, len(issues)), issues)
        detail = client.get(f"/api/v1/runs/{run_id}")
        response = client.get(f"/api/v1/runs/{run_id}/issues.csv")

    assert detail.status_code == 200
    assert len(detail.json()["issues"]) == 100
    assert response.status_code == 200, response.text
    assert response.headers["content-type"].startswith("text/csv")
    assert response.headers["content-disposition"] == (
        'attachment; filename="validation-issues.csv"'
    )
    rows = parse_csv_response(response)
    assert len(rows) == 105
    assert list(rows[0]) == ["row_number", "field_name", "code", "message"]
    assert rows[0]["row_number"] == "2"
    assert rows[-1]["row_number"] == "106"


def test_export_neutralizes_formula_prefixes_and_preserves_csv_content(tmp_path):
    db_path = str(tmp_path / "formula-export.db")
    run_id = "22222222-2222-4222-8222-222222222222"
    dangerous = [
        "=1+1",
        "+SUM(A1:A2)",
        "-2+3",
        "@SUM(A1:A2)",
        "  =HYPERLINK(\"https://example.invalid\")",
        "\t+CMD",
        "\r\n@FORMULA",
        "\v=VERTICAL_TAB",
        "\f@FORM_FEED",
        "\x00+NUL_PREFIX",
        "\u200b=ZERO_WIDTH",
    ]
    issues = [
        {
            "row_number": index + 2,
            "field_name": value,
            "code": value,
            "message": value,
        }
        for index, value in enumerate(dangerous)
    ]
    issues.append(
        {
            "row_number": 99,
            "field_name": "campo,unicode",
            "code": "SAFE",
            "message": 'Línea ñ, "citada"\nsegunda línea',
        }
    )

    with TestClient(create_app(db_path)) as client:
        store.save_run(db_path, sample_run(run_id, len(issues)), issues)
        response = client.get(f"/api/v1/runs/{run_id}/issues.csv")

    assert response.status_code == 200, response.text
    rows = parse_csv_response(response)
    for original, exported in zip(dangerous, rows[:-1], strict=True):
        for field in ("field_name", "code", "message"):
            assert exported[field].startswith("'")
            assert exported[field][1:] == original
    assert rows[-1]["field_name"] == "campo,unicode"
    assert rows[-1]["message"] == 'Línea ñ, "citada"\nsegunda línea'


def test_export_returns_404_for_unknown_run(tmp_path):
    with TestClient(create_app(str(tmp_path / "missing.db"))) as client:
        response = client.get("/api/v1/runs/unknown/issues.csv")

    assert response.status_code == 404
