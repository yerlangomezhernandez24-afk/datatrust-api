from scripts.benchmark_sqlite_journal import exercise_reader_writer


def test_delete_and_wal_reader_writer_experiment_is_deterministic(tmp_path):
    delete_result = exercise_reader_writer(tmp_path / "delete.sqlite3", "DELETE")
    wal_result = exercise_reader_writer(tmp_path / "wal.sqlite3", "WAL")

    assert delete_result["actual_journal_mode"] == "delete"
    assert delete_result["commit_result"] == "busy"
    assert delete_result["integrity_check"] == "ok"
    assert wal_result["actual_journal_mode"] == "wal"
    assert wal_result["commit_result"] == "committed"
    assert wal_result["integrity_check"] == "ok"
