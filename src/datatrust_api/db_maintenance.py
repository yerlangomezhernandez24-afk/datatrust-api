"""Mantenimiento SQLite local mediante APIs consistentes y sin sobrescritura."""

from __future__ import annotations

import sqlite3
from contextlib import closing
from dataclasses import dataclass
from pathlib import Path

from .store import SQLITE_BUSY_TIMEOUT_SECONDS, validate_db_path


class DatabaseIntegrityError(RuntimeError):
    """La base no pudo abrirse o no superó PRAGMA integrity_check."""


@dataclass(frozen=True)
class DatabaseCopyReport:
    source_integrity: str
    destination_integrity: str
    page_count: int


def _existing_database(path_value: str | Path) -> Path:
    validate_db_path(str(path_value))
    path = Path(path_value).resolve()
    if not path.is_file():
        raise FileNotFoundError("La base SQLite de origen no existe.")
    return path


def _read_only_connection(path: Path) -> sqlite3.Connection:
    return sqlite3.connect(
        f"{path.as_uri()}?mode=ro",
        uri=True,
        timeout=SQLITE_BUSY_TIMEOUT_SECONDS,
    )


def _integrity_from_connection(db: sqlite3.Connection) -> str:
    try:
        results = [row[0] for row in db.execute("PRAGMA integrity_check").fetchall()]
    except sqlite3.DatabaseError as exc:
        raise DatabaseIntegrityError(
            "La base SQLite no pudo superar la verificación de integridad."
        ) from exc
    if results != ["ok"]:
        raise DatabaseIntegrityError(
            "La base SQLite no superó la verificación de integridad."
        )
    if db.execute("PRAGMA foreign_key_check").fetchone() is not None:
        raise DatabaseIntegrityError(
            "La base SQLite no superó la verificación de integridad referencial."
        )
    return "ok"


def check_integrity(path_value: str | Path) -> str:
    """Verifica una base existente sin crear archivos ni modificar el journal."""
    path = _existing_database(path_value)
    try:
        with closing(_read_only_connection(path)) as db:
            return _integrity_from_connection(db)
    except sqlite3.DatabaseError as exc:
        raise DatabaseIntegrityError(
            "La base SQLite no pudo superar la verificación de integridad."
        ) from exc


def _copy_database(source_value: str | Path, destination_value: str | Path) -> DatabaseCopyReport:
    source = _existing_database(source_value)
    validate_db_path(str(destination_value))
    destination = Path(destination_value).resolve()
    if source == destination:
        raise ValueError("Las rutas de origen y destino deben ser distintas.")
    destination.parent.mkdir(parents=True, exist_ok=True)

    # La creación exclusiva reserva el nombre y garantiza que nunca se reemplace
    # una base, backup u otro archivo preexistente.
    with destination.open("xb"):
        pass
    created_destination = True
    try:
        source_integrity = check_integrity(source)
        with closing(_read_only_connection(source)) as source_db:
            with closing(
                sqlite3.connect(
                    destination,
                    timeout=SQLITE_BUSY_TIMEOUT_SECONDS,
                )
            ) as destination_db:
                source_db.backup(destination_db)
                destination_integrity = _integrity_from_connection(destination_db)
                page_count = destination_db.execute("PRAGMA page_count").fetchone()[0]
        return DatabaseCopyReport(
            source_integrity=source_integrity,
            destination_integrity=destination_integrity,
            page_count=page_count,
        )
    except Exception:
        if created_destination and destination.exists():
            destination.unlink()
        raise


def backup_database(source_value: str | Path, destination_value: str | Path) -> DatabaseCopyReport:
    """Crea un backup consistente con sqlite3.Connection.backup()."""
    return _copy_database(source_value, destination_value)


def restore_database(backup_value: str | Path, destination_value: str | Path) -> DatabaseCopyReport:
    """Restaura hacia una base nueva; nunca sobrescribe la base activa."""
    return _copy_database(backup_value, destination_value)
