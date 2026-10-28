import sqlite3
from concurrent.futures import ThreadPoolExecutor
from contextlib import closing
from threading import Barrier, Event

from fastapi.testclient import TestClient

from datatrust_api import store
from datatrust_api.main import create_app


def sample_run(run_id):
    return {
        "id": run_id,
        "filename": f"{run_id}.csv",
        "profile": "orders_v1",
        "status": "completed",
        "total_rows": 1,
        "valid_rows": 1,
        "invalid_rows": 0,
        "issue_count": 0,
        "created_at": "2026-10-25T00:00:00+00:00",
    }


def sample_issue(row_number):
    return {
        "row_number": row_number,
        "field_name": "email",
        "code": "INVALID_EMAIL",
        "message": "Formato de correo no reconocido.",
    }


def test_simultaneous_sqlite_writes_are_serialized_without_data_loss(tmp_path):
    db_path = str(tmp_path / "concurrent.db")
    worker_count = 6
    ready = Barrier(worker_count)
    store.init_db(db_path)

    def write(number):
        ready.wait(timeout=5)
        run = sample_run(f"run-{number}")
        run.update(valid_rows=0, invalid_rows=1, issue_count=1)
        store.save_run(db_path, run, [sample_issue(number + 2)])

    with ThreadPoolExecutor(max_workers=worker_count) as executor:
        futures = [executor.submit(write, number) for number in range(worker_count)]
        for future in futures:
            future.result(timeout=10)

    assert {run["id"] for run in store.list_runs(db_path, 100, 0)} == {
        f"run-{number}" for number in range(worker_count)
    }
    for number in range(worker_count):
        assert store.get_issues(db_path, f"run-{number}", 10, 0) == [
            sample_issue(number + 2)
        ]


def test_sqlite_connection_has_a_five_second_busy_timeout(tmp_path):
    db_path = str(tmp_path / "timeout.db")
    store.init_db(db_path)

    with closing(store.connect(db_path)) as db:
        busy_timeout = db.execute("PRAGMA busy_timeout").fetchone()[0]

    assert store.SQLITE_BUSY_TIMEOUT_SECONDS == 5.0
    assert busy_timeout == 5_000


class SignalingConnection:
    def __init__(self, connection, insert_started):
        self.connection = connection
        self.insert_started = insert_started

    def __getattr__(self, name):
        return getattr(self.connection, name)

    def __enter__(self):
        self.connection.__enter__()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return self.connection.__exit__(exc_type, exc_value, traceback)

    def execute(self, sql, parameters=()):
        if sql.lstrip().upper().startswith("INSERT INTO VALIDATION_RUNS"):
            self.insert_started.set()
        return self.connection.execute(sql, parameters)

    def close(self):
        self.connection.close()


def test_controlled_sqlite_lock_waits_and_completes_after_release(monkeypatch, tmp_path):
    db_path = str(tmp_path / "locked.db")
    store.init_db(db_path)
    locker = sqlite3.connect(db_path, timeout=0)
    locker.execute("BEGIN IMMEDIATE")
    insert_started = Event()
    original_connect = store.connect

    def signaling_connect(path):
        return SignalingConnection(original_connect(path), insert_started)

    monkeypatch.setattr(store, "connect", signaling_connect)

    try:
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(
                store.save_run, db_path, sample_run("after-lock-release"), []
            )
            assert insert_started.wait(timeout=2)
            assert not future.done()
            locker.rollback()
            future.result(timeout=10)
    finally:
        if locker.in_transaction:
            locker.rollback()
        locker.close()

    assert store.get_run(db_path, "after-lock-release") is not None


def test_reader_transaction_and_writer_complete_after_reader_release(monkeypatch, tmp_path):
    db_path = str(tmp_path / "reader-writer.db")
    store.init_db(db_path)
    store.save_run(db_path, sample_run("existing"), [])
    reader = sqlite3.connect(db_path, timeout=0)
    reader.execute("BEGIN")
    assert reader.execute("SELECT COUNT(*) FROM validation_runs").fetchone()[0] == 1
    insert_started = Event()
    original_connect = store.connect

    def signaling_connect(path):
        return SignalingConnection(original_connect(path), insert_started)

    monkeypatch.setattr(store, "connect", signaling_connect)

    try:
        with ThreadPoolExecutor(max_workers=1) as executor:
            future = executor.submit(
                store.save_run, db_path, sample_run("written-after-reader"), []
            )
            assert insert_started.wait(timeout=5)
            assert not future.done()
            reader.rollback()
            future.result(timeout=10)
    finally:
        if reader.in_transaction:
            reader.rollback()
        reader.close()

    assert store.get_run(db_path, "written-after-reader") is not None


def test_exhausted_sqlite_lock_returns_503_without_partial_persistence(
    monkeypatch, tmp_path
):
    db_path = str(tmp_path / "busy.db")
    app = create_app(db_path)

    with TestClient(app, raise_server_exceptions=False) as client:
        locker = sqlite3.connect(db_path, timeout=0)
        locker.execute("BEGIN IMMEDIATE")
        monkeypatch.setattr(store, "SQLITE_BUSY_TIMEOUT_SECONDS", 0.05)
        try:
            response = client.post(
                "/api/v1/runs",
                files={
                    "file": (
                        "orders.csv",
                        "order_id,customer_id,email,amount,currency,order_date\n"
                        "O1,C1,a@example.invalid,1,USD,2026-10-25\n",
                        "text/csv",
                    )
                },
            )
        finally:
            locker.rollback()
            locker.close()

        assert response.status_code == 503, response.text
        assert response.headers["retry-after"] == "1"
        assert client.get("/api/v1/runs").json() == []


def test_exhausted_exclusive_lock_on_read_returns_503_without_trace(
    monkeypatch, tmp_path
):
    db_path = str(tmp_path / "busy-read.db")
    app = create_app(db_path)

    with TestClient(app, raise_server_exceptions=False) as client:
        store.save_run(db_path, sample_run("existing"), [])
        locker = sqlite3.connect(db_path, timeout=0, isolation_level=None)
        locker.execute("BEGIN EXCLUSIVE")
        monkeypatch.setattr(store, "SQLITE_BUSY_TIMEOUT_SECONDS", 0.05)
        try:
            response = client.get("/api/v1/runs")
        finally:
            locker.rollback()
            locker.close()

    assert response.status_code == 503
    assert response.headers["retry-after"] == "1"
    assert response.json() == {
        "detail": "Almacenamiento local ocupado; intente nuevamente."
    }
    assert "Traceback" not in response.text
