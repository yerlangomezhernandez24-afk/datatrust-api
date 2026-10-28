"""Experimento reproducible de lector activo frente a commit DELETE/WAL."""

from __future__ import annotations

import argparse
import json
import platform
import sqlite3
import statistics
import tempfile
from contextlib import closing
from pathlib import Path
from time import perf_counter_ns


def exercise_reader_writer(path: Path, journal_mode: str) -> dict[str, object]:
    """Ejecuta un escenario coordinado sin sleeps ni carreras aleatorias."""
    if journal_mode.upper() not in {"DELETE", "WAL"}:
        raise ValueError("journal_mode debe ser DELETE o WAL.")
    if path.exists():
        raise FileExistsError(path)

    with closing(sqlite3.connect(path)) as setup:
        with setup:
            actual_mode = setup.execute(
                f"PRAGMA journal_mode={journal_mode.upper()}"
            ).fetchone()[0]
            setup.execute("PRAGMA synchronous=FULL")
            setup.execute(
                "CREATE TABLE events(id INTEGER PRIMARY KEY, value TEXT NOT NULL)"
            )
            setup.execute("INSERT INTO events(value) VALUES ('seed')")

    reader = sqlite3.connect(path, timeout=0, isolation_level=None)
    writer = sqlite3.connect(path, timeout=0, isolation_level=None)
    commit_result = "committed"
    try:
        reader.execute("BEGIN")
        reader.execute("SELECT COUNT(*) FROM events").fetchone()
        writer.execute("BEGIN IMMEDIATE")
        writer.execute("INSERT INTO events(value) VALUES ('synthetic')")
        started = perf_counter_ns()
        try:
            writer.commit()
        except sqlite3.OperationalError as exc:
            if getattr(exc, "sqlite_errorcode", None) != sqlite3.SQLITE_BUSY:
                raise
            commit_result = "busy"
            writer.rollback()
        elapsed_ms = (perf_counter_ns() - started) / 1_000_000
    finally:
        if reader.in_transaction:
            reader.rollback()
        if writer.in_transaction:
            writer.rollback()
        reader.close()
        writer.close()

    with closing(sqlite3.connect(path)) as verification:
        integrity = verification.execute("PRAGMA integrity_check").fetchone()[0]
        row_count = verification.execute("SELECT COUNT(*) FROM events").fetchone()[0]
        synchronous = verification.execute("PRAGMA synchronous").fetchone()[0]
    return {
        "requested_journal_mode": journal_mode.lower(),
        "actual_journal_mode": actual_mode,
        "commit_result": commit_result,
        "commit_attempt_ms": round(elapsed_ms, 6),
        "row_count": row_count,
        "integrity_check": integrity,
        "synchronous": synchronous,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repeats", type=int, default=10)
    args = parser.parse_args()
    if not 1 <= args.repeats <= 100:
        parser.error("--repeats debe estar entre 1 y 100")

    summary: dict[str, object] = {
        "python": platform.python_version(),
        "platform": platform.platform(),
        "sqlite": sqlite3.sqlite_version,
        "scenario": "reader transaction active while writer attempts commit",
        "repeats": args.repeats,
        "modes": {},
    }
    with tempfile.TemporaryDirectory(prefix="datatrust-journal-") as directory:
        root = Path(directory)
        for mode in ("DELETE", "WAL"):
            results = [
                exercise_reader_writer(root / f"{mode.lower()}-{index}.sqlite3", mode)
                for index in range(args.repeats)
            ]
            summary["modes"][mode.lower()] = {
                "actual_journal_mode": results[0]["actual_journal_mode"],
                "committed": sum(result["commit_result"] == "committed" for result in results),
                "busy": sum(result["commit_result"] == "busy" for result in results),
                "median_commit_attempt_ms": round(
                    statistics.median(result["commit_attempt_ms"] for result in results),
                    6,
                ),
                "integrity_checks": sorted({result["integrity_check"] for result in results}),
                "synchronous": results[0]["synchronous"],
            }
    print(json.dumps(summary, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
