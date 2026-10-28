"""Exportación CSV segura de incidencias ya persistidas."""

from __future__ import annotations

import csv
import io
import unicodedata
from collections.abc import Iterable, Iterator
from typing import Any

EXPORT_FIELDS = ("row_number", "field_name", "code", "message")
FORMULA_PREFIXES = ("=", "+", "-", "@")


def _formula_candidate(text: str) -> str:
    """Omite solo para inspección whitespace y controles/formato iniciales."""
    index = 0
    while index < len(text):
        character = text[index]
        if not (
            character.isspace()
            or unicodedata.category(character) in {"Cc", "Cf"}
        ):
            break
        index += 1
    return text[index:]


def safe_csv_cell(value: Any) -> str:
    """Prefija texto que una hoja de cálculo podría interpretar como fórmula."""
    text = str(value)
    candidate = _formula_candidate(text)
    if candidate.startswith(FORMULA_PREFIXES):
        return "'" + text
    return text


def iter_issue_csv(issues: Iterable[dict]) -> Iterator[bytes]:
    """Genera UTF-8 con BOM, una fila a la vez, sin cargar todo el CSV."""
    stream = io.StringIO(newline="")
    writer = csv.writer(stream, lineterminator="\r\n")

    writer.writerow(EXPORT_FIELDS)
    yield b"\xef\xbb\xbf" + stream.getvalue().encode("utf-8")

    for issue in issues:
        stream.seek(0)
        stream.truncate(0)
        writer.writerow([safe_csv_cell(issue[field]) for field in EXPORT_FIELDS])
        yield stream.getvalue().encode("utf-8")
