import sqlite3

import pytest

from datatrust_api import store
from datatrust_api.db_maintenance import (
    DatabaseIntegrityError,
    backup_database,
    check_integrity,
    restore_database,
)


def sample_run(run_id):
    return {
        "id": run_id,
        "filename": f"{run_id}.csv",
        "profile": "orders_v1",
        "status": "completed",
        "total_rows": 1,
        "valid_rows": 0,
        "invalid_rows": 1,
        "issue_count": 1,
        "created_at": "2026-10-27T00:00:00+00:00",
    }


def sample_issue():
    return {
        "row_number": 2,
        "field_name": "amount",
        "code": "INVALID_AMOUNT",
        "message": "El importe no cumple formato, rango o escala del perfil.",
    }


def test_backup_and_restore_round_trip_uses_distinct_database(tmp_path):
    source = tmp_path / "source.sqlite3"
    backup = tmp_path / "backup.sqlite3"
    restored = tmp_path / "restored.sqlite3"
    store.init_db(str(source))
    store.save_run(str(source), sample_run("before-backup"), [sample_issue()])

    backup_report = backup_database(source, backup)
    store.save_run(str(source), sample_run("after-backup"), [sample_issue()])
    restore_report = restore_database(backup, restored)

    assert backup_report.source_integrity == "ok"
    assert backup_report.destination_integrity == "ok"
    assert restore_report.source_integrity == "ok"
    assert restore_report.destination_integrity == "ok"
    assert check_integrity(source) == "ok"
    assert check_integrity(backup) == "ok"
    assert check_integrity(restored) == "ok"
    assert store.get_run(str(restored), "before-backup") is not None
    assert store.get_run(str(restored), "after-backup") is None
    assert len(store.get_issues(str(restored), "before-backup", 10, 0)) == 1


def test_backup_refuses_to_overwrite_existing_destination(tmp_path):
    source = tmp_path / "source.sqlite3"
    destination = tmp_path / "existing.sqlite3"
    store.init_db(str(source))
    destination.write_bytes(b"do-not-overwrite")

    with pytest.raises(FileExistsError):
        backup_database(source, destination)

    assert destination.read_bytes() == b"do-not-overwrite"


def test_backup_rejects_missing_or_same_source_without_creating_output(tmp_path):
    missing = tmp_path / "missing.sqlite3"
    destination = tmp_path / "destination.sqlite3"

    with pytest.raises(FileNotFoundError):
        backup_database(missing, destination)
    assert not destination.exists()

    source = tmp_path / "source.sqlite3"
    store.init_db(str(source))
    with pytest.raises(ValueError, match="distintas"):
        backup_database(source, source)


def test_integrity_check_rejects_corrupt_database_without_echoing_content(tmp_path):
    corrupt = tmp_path / "corrupt.sqlite3"
    marker = b"PRIVATE_CORRUPT_MARKER"
    corrupt.write_bytes(marker)

    with pytest.raises(DatabaseIntegrityError) as error:
        check_integrity(corrupt)

    assert marker.decode() not in str(error.value)


def test_integrity_check_detects_foreign_key_violation(tmp_path):
    database = tmp_path / "foreign-key.sqlite3"
    store.init_db(str(database))
    with sqlite3.connect(database) as db:
        db.execute(
            "INSERT INTO validation_issues(run_id,row_number,field_name,code,message) "
            "VALUES ('missing-run',2,'amount','INVALID_AMOUNT','Mensaje estático.')"
        )

    with pytest.raises(DatabaseIntegrityError, match="referencial"):
        check_integrity(database)


def test_backup_is_consistent_while_source_connection_remains_open(tmp_path):
    source = tmp_path / "source.sqlite3"
    backup = tmp_path / "online-backup.sqlite3"
    store.init_db(str(source))
    store.save_run(str(source), sample_run("committed"), [sample_issue()])

    open_reader = sqlite3.connect(source)
    try:
        assert open_reader.execute("SELECT COUNT(*) FROM validation_runs").fetchone()[0] == 1
        report = backup_database(source, backup)
    finally:
        open_reader.close()

    assert report.destination_integrity == "ok"
    assert store.get_run(str(backup), "committed") is not None
