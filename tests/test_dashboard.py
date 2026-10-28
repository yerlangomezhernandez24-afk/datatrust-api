from fastapi.testclient import TestClient

from datatrust_api.main import create_app


CSV_WITH_ISSUE = (
    "order_id,customer_id,email,amount,currency,order_date\n"
    "O1,C1,invalid-email,10,USD,2026-10-25\n"
)


def test_dashboard_and_local_assets_are_served(tmp_path):
    with TestClient(create_app(str(tmp_path / "dashboard.db"))) as client:
        page = client.get("/")
        javascript = client.get("/static/app.js")
        stylesheet = client.get("/static/styles.css")
        sample = client.get("/static/sample-orders.csv")
        favicon = client.get("/static/favicon.svg")

    assert page.status_code == 200
    assert "DataTrust API" in page.text
    assert 'id="upload-form"' in page.text
    assert 'for="csv-file"' in page.text
    assert 'id="profile"' in page.text
    assert 'aria-describedby="file-help selected-file"' in page.text
    assert 'role="status"' in page.text
    assert 'aria-live="polite"' in page.text
    assert 'id="app-health"' in page.text
    assert 'id="quick-start-title"' in page.text
    assert "desliza la tabla horizontalmente" in page.text
    assert 'href="/static/sample-orders.csv"' in page.text
    assert "Demo local" in page.text
    assert page.text.count('scope="col"') == 4
    assert javascript.status_code == 200
    assert "/api/v1/profiles" in javascript.text
    assert "/api/v1/runs" in javascript.text
    assert "/issues.csv" in javascript.text
    assert "innerHTML" not in javascript.text
    assert "localStorage" not in javascript.text
    assert "sessionStorage" not in javascript.text
    assert "formElement.reset()" not in javascript.text
    assert 'fileInput.value = ""' in javascript.text
    assert "RUN_LIMIT + 1" in javascript.text
    assert "ISSUE_LIMIT + 1" in javascript.text
    assert 'setAttribute("aria-busy", String(isBusy))' in javascript.text
    assert 'setAttribute("role", kind === "error" ? "alert" : "status")' in javascript.text
    assert 'run.valid_rows === 1 ? "fila válida" : "filas válidas"' in javascript.text
    assert stylesheet.status_code == 200
    assert "@media" in stylesheet.text
    assert ":focus-visible" in stylesheet.text
    assert ".workspace > .panel" in stylesheet.text
    assert "min-width: 0" in stylesheet.text
    assert "linear-gradient" not in stylesheet.text
    assert "--space-" in stylesheet.text
    assert ".brand, .inline-link, .skip-link:focus" in stylesheet.text
    assert sample.status_code == 200
    assert sample.text.startswith(
        "order_id,customer_id,email,amount,currency,order_date"
    )
    assert "DEMO-1002" in sample.text
    assert favicon.status_code == 200
    assert favicon.headers["content-type"].startswith("image/svg+xml")


def test_dashboard_backend_flow_is_connected_end_to_end(tmp_path):
    with TestClient(create_app(str(tmp_path / "dashboard-flow.db"))) as client:
        profiles = client.get("/api/v1/profiles")
        created = client.post(
            "/api/v1/runs?profile=orders_v1",
            files={"file": ("orders.csv", CSV_WITH_ISSUE, "text/csv")},
        )
        run_id = created.json()["id"]
        listed = client.get("/api/v1/runs?limit=20&offset=0")
        detail = client.get(f"/api/v1/runs/{run_id}")
        issues = client.get(f"/api/v1/runs/{run_id}/issues?limit=100&offset=0")
        export = client.get(f"/api/v1/runs/{run_id}/issues.csv")

    assert profiles.status_code == 200
    assert created.status_code == 201, created.text
    assert created.json()["issue_count"] == 1
    assert any(run["id"] == run_id for run in listed.json())
    assert detail.json()["id"] == run_id
    assert [issue["code"] for issue in issues.json()] == ["INVALID_EMAIL"]
    assert export.status_code == 200
    assert b"INVALID_EMAIL" in export.content
