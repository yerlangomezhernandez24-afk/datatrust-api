from importlib.resources import files
from pathlib import Path

from fastapi.testclient import TestClient

from datatrust_api.main import MAX_FILE_BYTES, create_app
from datatrust_api.validator import validate_orders_csv


EXPECTED_DEMOS = {
    "demo-orders-6.csv": (6, 2, 5),
    "demo-orders-100.csv": (100, 90, 10),
}


def demo_bytes(filename: str) -> bytes:
    return files("datatrust_api").joinpath("static", filename).read_bytes()


def test_packaged_portfolio_demos_have_documented_deterministic_results():
    for filename, expected in EXPECTED_DEMOS.items():
        payload = demo_bytes(filename)

        total, valid, issues = validate_orders_csv(payload)

        assert (total, valid, len(issues)) == expected
        assert len(payload) <= MAX_FILE_BYTES
        assert b"example.invalid" in payload


def test_hundred_order_demo_has_ten_distinct_invalid_rows_and_ten_issues():
    total, valid, issues = validate_orders_csv(demo_bytes("demo-orders-100.csv"))

    assert (total, valid, len(issues)) == (100, 90, 10)
    assert len({issue["row_number"] for issue in issues}) == 10
    assert {issue["code"] for issue in issues} == {"INVALID_EMAIL"}


def test_portfolio_demos_can_be_downloaded_and_processed_end_to_end(tmp_path):
    with TestClient(create_app(str(tmp_path / "portfolio.db"))) as client:
        dashboard = client.get("/")
        assert 'href="/static/demo-orders-6.csv"' in dashboard.text
        assert 'href="/static/demo-orders-100.csv"' in dashboard.text

        for filename, (total, valid, issue_count) in EXPECTED_DEMOS.items():
            download = client.get(f"/static/{filename}")
            assert download.status_code == 200
            created = client.post(
                "/api/v1/runs?profile=orders_v1",
                files={"file": (filename, download.content, "text/csv")},
            )
            assert created.status_code == 201, created.text
            assert created.json()["total_rows"] == total
            assert created.json()["valid_rows"] == valid
            assert created.json()["invalid_rows"] == total - valid
            assert created.json()["issue_count"] == issue_count

        assert len(client.get("/api/v1/runs?limit=100").json()) == 2


def test_windows_demo_launcher_is_local_explicit_and_does_not_change_policy():
    script = (
        Path(__file__).parents[1] / "scripts" / "iniciar_demo.ps1"
    ).read_text(encoding="utf-8")

    assert "127.0.0.1" in script
    assert "--workers 1" in script
    assert ".venv\\Scripts\\python.exe" in script
    assert "Test-Path -LiteralPath" in script
    assert "Set-ExecutionPolicy" not in script
    assert "Invoke-WebRequest" not in script
