import sqlite3

import pytest
from fastapi.testclient import TestClient

from datatrust_api import main as main_module
from datatrust_api.main import MAX_FILE_BYTES, create_app

HEAD = "order_id,customer_id,email,amount,currency,order_date\n"
ROWS = "O1,C1,a@example.org,20,CRC,2026-10-25\nO1,C2,b@example.org,-2,USD,2026-10-25\n"


def test_end_to_end_persistence(tmp_path):
    app = create_app(str(tmp_path / "runs.db"))
    with TestClient(app) as client:
        r = client.post("/api/v1/runs", files={"file": ("orders.csv", HEAD + ROWS, "text/csv")})
        assert r.status_code == 201, r.text
        result = r.json()
        assert result["total_rows"] == 2
        assert result["valid_rows"] == 1
        assert result["invalid_rows"] == 1
        assert result["issue_count"] == 2
        run_id = result["id"]
        got = client.get(f"/api/v1/runs/{run_id}")
        assert got.status_code == 200
        assert {x["code"] for x in got.json()["issues"]} == {"DUPLICATE", "INVALID_AMOUNT"}
        assert len(client.get(f"/api/v1/runs/{run_id}/issues").json()) == 2
        assert len(client.get("/api/v1/runs").json()) == 1
        assert client.get("/health").json()["status"] == "ok"
        assert client.get("/openapi.json").status_code == 200
    with TestClient(create_app(str(tmp_path / "runs.db"))) as client:
        assert client.get(f"/api/v1/runs/{run_id}").status_code == 200


def test_invalid_schema_and_unknown_id(tmp_path):
    with TestClient(create_app(str(tmp_path / "runs.db"))) as client:
        r = client.post("/api/v1/runs", files={"file": ("x.csv", "not,csv\nhello,world\n", "text/csv")})
        assert r.status_code == 422
        assert client.get("/api/v1/runs/does-not-exist").status_code == 404
        assert client.get("/api/v1/runs/does-not-exist/issues").status_code == 404
        assert client.get("/api/v1/runs").json() == []


def test_reject_wrong_extension(tmp_path):
    with TestClient(create_app(str(tmp_path / "runs.db"))) as client:
        r = client.post("/api/v1/runs", files={"file": ("payload.txt", HEAD, "text/plain")})
        assert r.status_code == 415


def test_reject_disguised_extension_before_handling_long_name(tmp_path):
    disguised_name = "a" * 156 + ".csv.exe"
    with TestClient(create_app(str(tmp_path / "runs.db"))) as client:
        response = client.post(
            "/api/v1/runs",
            files={"file": (disguised_name, HEAD, "text/csv")},
        )
    assert response.status_code == 415


def test_accept_long_filename_when_real_extension_is_csv(tmp_path):
    long_name = "a" * 200 + ".csv"
    with TestClient(create_app(str(tmp_path / "runs.db"))) as client:
        response = client.post(
            "/api/v1/runs",
            files={"file": (long_name, HEAD, "text/csv")},
        )
    assert response.status_code == 201, response.text


def test_original_filename_is_not_stored_or_exposed(tmp_path):
    db_path = tmp_path / "runs.db"
    sensitive_name = "secret-user@example.invalid-orders.csv"
    with TestClient(create_app(str(db_path))) as client:
        response = client.post(
            "/api/v1/runs",
            files={"file": (sensitive_name, HEAD, "text/csv")},
        )
        assert response.status_code == 201, response.text
        result = response.json()
        assert result["filename"] == f"{result['id']}.csv"
        assert sensitive_name not in response.text
        assert sensitive_name not in client.get(f"/api/v1/runs/{result['id']}").text

    with sqlite3.connect(db_path) as db:
        stored_filename = db.execute(
            "SELECT filename FROM validation_runs WHERE id=?", (result["id"],)
        ).fetchone()[0]
    assert stored_filename == f"{result['id']}.csv"
    assert sensitive_name not in stored_filename


def test_reject_large_file(tmp_path):
    with TestClient(create_app(str(tmp_path / "runs.db"))) as client:
        r = client.post("/api/v1/runs", files={"file": ("oversize.csv", b"a" * (MAX_FILE_BYTES + 1), "text/csv")})
        assert r.status_code == 413


def test_empty_file_is_a_structural_422_without_persistence(tmp_path):
    with TestClient(create_app(str(tmp_path / "empty.db"))) as client:
        response = client.post(
            "/api/v1/runs",
            files={"file": ("empty.csv", b"", "text/csv")},
        )

        assert response.status_code == 422
        assert response.json()["detail"] == "El archivo CSV está vacío."
        assert client.get("/api/v1/runs").json() == []


def test_client_mime_is_only_a_hint_and_extension_and_csv_structure_remain_authority(
    tmp_path,
):
    with TestClient(create_app(str(tmp_path / "mime.db"))) as client:
        valid_with_generic_mime = client.post(
            "/api/v1/runs",
            files={"file": ("orders.csv", HEAD, "application/octet-stream")},
        )
        disguised_as_csv_mime = client.post(
            "/api/v1/runs",
            files={"file": ("orders.exe", HEAD, "text/csv")},
        )
        json_in_csv = client.post(
            "/api/v1/runs",
            files={"file": ("payload.csv", b'{"not":"csv"}', "text/csv")},
        )

    assert valid_with_generic_mime.status_code == 201
    assert disguised_as_csv_mime.status_code == 415
    assert json_in_csv.status_code == 422


def test_local_security_headers_and_private_paths(tmp_path):
    with TestClient(create_app(str(tmp_path / "headers.db"))) as client:
        dashboard = client.get("/")
        health = client.get("/health")
        private = client.get("/static/../pyproject.toml")

    for response in (dashboard, health, private):
        assert response.headers["x-content-type-options"] == "nosniff"
        assert response.headers["referrer-policy"] == "no-referrer"
        assert response.headers["x-frame-options"] == "DENY"
    assert private.status_code == 404


def test_limit_query_restrictions(tmp_path):
    with TestClient(create_app(str(tmp_path / "runs.db"))) as client:
        assert client.get("/api/v1/runs?limit=101").status_code == 422
        assert client.get("/api/v1/runs?offset=-1").status_code == 422
        too_large = 2**63
        assert client.get(f"/api/v1/runs?offset={too_large}").status_code == 422
        assert client.get(f"/api/v1/runs/unknown/issues?offset={too_large}").status_code == 422


def test_reject_in_memory_sqlite_at_startup():
    app = create_app(":memory:")
    with pytest.raises(ValueError, match="memoria"):
        with TestClient(app):
            pass


def test_post_delegates_blocking_work_to_threadpool(monkeypatch, tmp_path):
    delegated_functions = []

    async def tracking_threadpool(func, *args, **kwargs):
        delegated_functions.append(func.__name__)
        return func(*args, **kwargs)

    monkeypatch.setattr(main_module, "run_in_threadpool", tracking_threadpool, raising=False)
    with TestClient(create_app(str(tmp_path / "runs.db"))) as client:
        response = client.post(
            "/api/v1/runs",
            files={"file": ("orders.csv", HEAD, "text/csv")},
        )

    assert response.status_code == 201, response.text
    assert delegated_functions == ["validate_orders_csv", "save_run"]
