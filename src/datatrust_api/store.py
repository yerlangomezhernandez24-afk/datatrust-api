"""Persistencia de resúmenes e incidencias con SQLite (sin filas originales)."""
from __future__ import annotations

import sqlite3
from collections.abc import Iterator
from contextlib import closing, contextmanager
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS validation_runs (
    id TEXT PRIMARY KEY, filename TEXT NOT NULL, profile TEXT NOT NULL,
    status TEXT NOT NULL, total_rows INTEGER NOT NULL, valid_rows INTEGER NOT NULL,
    invalid_rows INTEGER NOT NULL, issue_count INTEGER NOT NULL, created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS validation_issues (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id TEXT NOT NULL REFERENCES validation_runs(id) ON DELETE CASCADE,
    row_number INTEGER NOT NULL, field_name TEXT NOT NULL,
    code TEXT NOT NULL, message TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_issues_run_id ON validation_issues(run_id);
"""

SQLITE_BUSY_TIMEOUT_SECONDS = 5.0


class StorageBusyError(RuntimeError):
    """Una operación no obtuvo el bloqueo SQLite dentro del plazo configurado."""


def _is_busy_error(exc: sqlite3.OperationalError) -> bool:
    error_code = getattr(exc, "sqlite_errorcode", None)
    return error_code is not None and (error_code & 0xFF) in {
        sqlite3.SQLITE_BUSY,
        sqlite3.SQLITE_LOCKED,
    }


@contextmanager
def connection(db_path: str) -> Iterator[sqlite3.Connection]:
    """Cierra siempre y traduce contención esperada de lectura o escritura."""
    try:
        with closing(connect(db_path)) as db:
            yield db
    except sqlite3.OperationalError as exc:
        if _is_busy_error(exc):
            raise StorageBusyError(
                "SQLite permaneció bloqueado hasta agotar el tiempo de espera."
            ) from exc
        raise


def validate_db_path(db_path: str) -> str:
    if not db_path.strip():
        raise ValueError("La ruta de SQLite no puede estar vacía.")
    if db_path.strip().casefold() == ":memory:":
        raise ValueError(
            "SQLite en memoria no es compatible con esta arquitectura; "
            "configure DATATRUST_DB con una ruta de archivo."
        )
    return db_path


def connect(db_path: str) -> sqlite3.Connection:
    db_path = validate_db_path(db_path)
    db = sqlite3.connect(db_path, timeout=SQLITE_BUSY_TIMEOUT_SECONDS)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    return db


def init_db(db_path: str) -> None:
    db_path = validate_db_path(db_path)
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    with connection(db_path) as db:
        with db:
            db.executescript(SCHEMA)


def save_run(db_path: str, run: dict, issues: list[dict]) -> None:
    with connection(db_path) as db:
        with db:
            db.execute(
                "INSERT INTO validation_runs(id,filename,profile,status,total_rows,valid_rows,invalid_rows,issue_count,created_at) "
                "VALUES (:id,:filename,:profile,:status,:total_rows,:valid_rows,:invalid_rows,:issue_count,:created_at)",
                run,
            )
            db.executemany(
                "INSERT INTO validation_issues(run_id,row_number,field_name,code,message) "
                "VALUES (:run_id,:row_number,:field_name,:code,:message)",
                [dict(issue, run_id=run["id"]) for issue in issues],
            )


def get_run(db_path: str, run_id: str) -> dict | None:
    with connection(db_path) as db:
        row = db.execute("SELECT * FROM validation_runs WHERE id=?", (run_id,)).fetchone()
        return dict(row) if row else None


def list_runs(db_path: str, limit: int, offset: int) -> list[dict]:
    with connection(db_path) as db:
        records = db.execute(
            "SELECT * FROM validation_runs ORDER BY created_at DESC, id DESC LIMIT ? OFFSET ?",
            (limit, offset),
        ).fetchall()
        return [dict(r) for r in records]


def get_issues(db_path: str, run_id: str, limit: int, offset: int) -> list[dict]:
    with connection(db_path) as db:
        records = db.execute(
            "SELECT row_number,field_name,code,message FROM validation_issues WHERE run_id=? "
            "ORDER BY id ASC LIMIT ? OFFSET ?", (run_id, limit, offset)
        ).fetchall()
        return [dict(r) for r in records]


def iter_issues(db_path: str, run_id: str, batch_size: int = 500) -> Iterator[dict]:
    """Itera incidencias ordenadas en lotes y cierra la conexión al finalizar."""
    with connection(db_path) as db:
        cursor = db.execute(
            "SELECT row_number,field_name,code,message FROM validation_issues "
            "WHERE run_id=? ORDER BY id ASC",
            (run_id,),
        )
        while records := cursor.fetchmany(batch_size):
            for record in records:
                yield dict(record)
