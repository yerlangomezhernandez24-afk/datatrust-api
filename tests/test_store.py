import sqlite3

import pytest

from datatrust_api import store


class TrackingConnection:
    """Conserva una referencia para comprobar que store cierre la conexión."""

    def __init__(self, connection):
        self.connection = connection
        self.closed = False

    def __getattr__(self, name):
        return getattr(self.connection, name)

    def __enter__(self):
        self.connection.__enter__()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return self.connection.__exit__(exc_type, exc_value, traceback)

    def close(self):
        self.closed = True
        self.connection.close()


def sample_run(run_id="run-1"):
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


def install_connection_tracker(monkeypatch):
    original_connect = store.connect
    opened = []

    def tracked_connect(db_path):
        connection = TrackingConnection(original_connect(db_path))
        opened.append(connection)
        return connection

    monkeypatch.setattr(store, "connect", tracked_connect)
    return opened


def close_test_connections(opened):
    for connection in opened:
        if not connection.closed:
            connection.close()


def test_store_closes_every_connection_after_success(monkeypatch, tmp_path):
    db_path = str(tmp_path / "runs.db")
    opened = install_connection_tracker(monkeypatch)

    try:
        store.init_db(db_path)
        store.save_run(db_path, sample_run(), [])
        assert store.get_run(db_path, "run-1") is not None
        assert len(store.list_runs(db_path, 20, 0)) == 1
        assert store.get_issues(db_path, "run-1", 100, 0) == []
        assert opened and all(connection.closed for connection in opened)
    finally:
        close_test_connections(opened)


def test_save_run_rolls_back_and_closes_connection_on_error(monkeypatch, tmp_path):
    db_path = str(tmp_path / "runs.db")
    store.init_db(db_path)
    opened = install_connection_tracker(monkeypatch)
    invalid_issue = {
        "row_number": None,
        "field_name": "email",
        "code": "INVALID_EMAIL",
        "message": "Formato de correo no reconocido.",
    }

    try:
        with pytest.raises(sqlite3.IntegrityError):
            store.save_run(db_path, sample_run("rollback-run"), [invalid_issue])
        was_closed = opened[-1].closed
    finally:
        close_test_connections(opened)

    with sqlite3.connect(db_path) as db:
        persisted = db.execute(
            "SELECT COUNT(*) FROM validation_runs WHERE id=?", ("rollback-run",)
        ).fetchone()[0]

    assert was_closed
    assert persisted == 0
