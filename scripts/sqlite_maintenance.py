"""CLI local para integridad, backup y restauración segura de SQLite."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict

from datatrust_api.db_maintenance import (
    backup_database,
    check_integrity,
    restore_database,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Mantenimiento SQLite local; los destinos nunca se sobrescriben."
    )
    subparsers = parser.add_subparsers(dest="operation", required=True)

    check = subparsers.add_parser("check")
    check.add_argument("database")

    for operation in ("backup", "restore"):
        command = subparsers.add_parser(operation)
        command.add_argument("source")
        command.add_argument("destination")

    args = parser.parse_args()
    if args.operation == "check":
        print(json.dumps({"integrity": check_integrity(args.database)}))
    else:
        function = backup_database if args.operation == "backup" else restore_database
        print(json.dumps(asdict(function(args.source, args.destination))))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
