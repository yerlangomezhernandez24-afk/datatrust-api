"""Comprueba que las versiones declaradas por el proyecto sean coherentes."""

from __future__ import annotations

import argparse
import importlib.metadata
import sys
import tomllib
from pathlib import Path

from datatrust_api import __version__
from datatrust_api.main import app


ROOT = Path(__file__).resolve().parents[1]


def project_version() -> str:
    with (ROOT / "pyproject.toml").open("rb") as source:
        return tomllib.load(source)["project"]["version"]


def version_report(*, include_installed: bool) -> dict[str, str]:
    expected = project_version()
    report = {
        "pyproject": expected,
        "package": __version__,
        "fastapi": app.version,
    }
    if include_installed:
        try:
            report["installed_metadata"] = importlib.metadata.version("datatrust-api")
        except importlib.metadata.PackageNotFoundError:
            report["installed_metadata"] = "<not-installed>"
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--installed",
        action="store_true",
        help="Incluye metadata de la distribución instalada (útil después de pip install).",
    )
    args = parser.parse_args()
    report = version_report(include_installed=args.installed)
    expected = report["pyproject"]
    for source, value in report.items():
        print(f"{source}={value}")
    mismatches = {
        source: value
        for source, value in report.items()
        if source != "pyproject" and value != expected
    }
    if mismatches:
        print(
            "Version mismatch: "
            + ", ".join(f"{source}={value}" for source, value in mismatches.items()),
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
