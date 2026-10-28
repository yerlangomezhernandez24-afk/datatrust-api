"""Reglas deterministas para el perfil de demostración orders_v1.

Este módulo no pretende validar direcciones de correo con exactitud RFC completa
ni inferir fraude. Evalúa reglas explícitas, medibles y reproducibles.
"""

from __future__ import annotations

import csv
import io
import re
import unicodedata
from datetime import date
from decimal import Decimal, InvalidOperation

from .profiles import ValidationProfile, get_profile

REQUIRED_FIELDS = ("order_id", "customer_id", "email", "amount", "currency", "order_date")
ALLOWED_CURRENCIES = {"CRC", "USD", "EUR"}
MAX_ROWS = 10_000
EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")
DECIMAL_PATTERN = re.compile(r"^[0-9]+(?:\.[0-9]+)?$")
MAX_CSV_FIELD_CHARACTERS = 2 * 1024 * 1024
MAX_HEADER_CHARACTERS = 64
MAX_HEADER_UTF8_BYTES = 256
MAX_EXTRA_FIELD_CHARACTERS = 4_096
MAX_EXTRA_FIELD_UTF8_BYTES = 16_384

# El archivo completo ya está limitado a 2 MiB. Elevar el techo del parser permite
# emitir incidencias de política más claras que su valor implícito de 131.072.
csv.field_size_limit(MAX_CSV_FIELD_CHARACTERS)


class InvalidDataset(ValueError):
    """Formato del archivo CSV no compatible o limitación excedida."""


def _has_control_or_format_character(value: str) -> bool:
    """Evita caracteres invisibles/de control en campos con sintaxis externa."""
    return any(unicodedata.category(character) in {"Cc", "Cf"} for character in value)


def validate_orders_csv(
    data: bytes,
    profile: ValidationProfile | None = None,
) -> tuple[int, int, list[dict]]:
    """Devuelve (filas totales, filas válidas, incidencias); no almacena filas crudas."""
    profile = profile or get_profile("orders_v1")
    try:
        content = data.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise InvalidDataset("El archivo debe tener codificación UTF-8.") from exc

    reader = csv.reader(io.StringIO(content, newline=""), strict=True)
    try:
        header = next(reader)
    except StopIteration as exc:
        raise InvalidDataset("El archivo CSV está vacío.") from exc
    except csv.Error as exc:
        raise InvalidDataset("Encabezado CSV mal formado.") from exc

    header = [unicodedata.normalize("NFC", h.strip()) for h in header]
    if any(_has_control_or_format_character(name) for name in header):
        raise InvalidDataset(
            "El encabezado contiene caracteres Unicode de control o formato."
        )
    if any(
        len(name) > MAX_HEADER_CHARACTERS
        or len(name.encode("utf-8")) > MAX_HEADER_UTF8_BYTES
        for name in header
    ):
        raise InvalidDataset(
            "Cada nombre de columna admite hasta 64 caracteres y 256 bytes UTF-8."
        )
    if len(header) != len(set(header)) or any(not h for h in header):
        raise InvalidDataset("El encabezado tiene columnas vacías o repetidas.")
    missing = sorted(set(profile.required_fields) - set(header))
    if missing:
        raise InvalidDataset("Faltan columnas obligatorias: " + ", ".join(missing))

    total_rows, valid_rows = 0, 0
    issues: list[dict] = []
    seen_values: dict[str, set[str]] = {
        field: set() for field in profile.unique_fields
    }

    try:
        for number, cells in enumerate(reader, start=2):
            total_rows += 1
            if total_rows > profile.max_rows:
                raise InvalidDataset(f"El límite de filas es {profile.max_rows}.")
            row_issues: list[dict] = []

            def add_issue(field: str, code: str, message: str) -> None:
                row_issues.append({
                    "row_number": number, "field_name": field,
                    "code": code, "message": message,
                })

            if len(cells) != len(header):
                add_issue("_row", "COLUMN_COUNT", "La cantidad de columnas no coincide con el encabezado.")
            row = dict(zip(header, cells))
            vals = {
                key: (row.get(key) or "").strip()
                for key in profile.required_fields
            }
            invalid_length_fields: set[str] = set()
            for index, cell in enumerate(cells):
                field = header[index] if index < len(header) else "_row"
                value = (cell or "").strip()
                limit = profile.field_limits.get(field)
                max_characters = (
                    limit.max_characters
                    if limit is not None
                    else MAX_EXTRA_FIELD_CHARACTERS
                )
                max_utf8_bytes = (
                    limit.max_utf8_bytes
                    if limit is not None
                    else MAX_EXTRA_FIELD_UTF8_BYTES
                )
                if (
                    len(value) > max_characters
                    or len(value.encode("utf-8")) > max_utf8_bytes
                ):
                    issue_field = field if limit is not None else "_extra"
                    add_issue(
                        issue_field,
                        "VALUE_TOO_LONG",
                        "El valor supera el límite de longitud del perfil.",
                    )
                    invalid_length_fields.add(field)
            for key, value in vals.items():
                if not value:
                    add_issue(key, "REQUIRED", "Valor obligatorio ausente.")

            invalid_identifiers: set[str] = set()
            for field in profile.identifier_fields:
                if vals[field] and _has_control_or_format_character(vals[field]):
                    add_issue(
                        field,
                        "INVALID_IDENTIFIER",
                        "El identificador contiene caracteres no permitidos.",
                    )
                    invalid_identifiers.add(field)

            for field in profile.unique_fields:
                unique_value = unicodedata.normalize("NFC", vals[field]).casefold()
                if (
                    unique_value
                    and field not in invalid_length_fields
                    and field not in invalid_identifiers
                ):
                    if unique_value in seen_values[field]:
                        add_issue(field, "DUPLICATE", "Valor repetido para un campo único.")
                    seen_values[field].add(unique_value)

            for field in profile.email_fields:
                if field not in invalid_length_fields and vals[field] and (
                    _has_control_or_format_character(vals[field])
                    or not EMAIL_PATTERN.fullmatch(vals[field])
                ):
                    add_issue(field, "INVALID_EMAIL", "Formato de correo no reconocido.")

            for field, policy in profile.decimal_policies.items():
                if field not in invalid_length_fields and vals[field]:
                    try:
                        text = vals[field]
                        if DECIMAL_PATTERN.fullmatch(text) is None:
                            raise InvalidOperation
                        amount = Decimal(text)
                        currency = vals[policy.currency_field].upper()
                        maximum_places = policy.max_decimal_places_by_currency.get(
                            currency,
                            max(policy.max_decimal_places_by_currency.values()),
                        )
                        decimal_places = len(text.partition(".")[2])
                        if (
                            not amount.is_finite()
                            or not policy.minimum <= amount <= policy.maximum
                            or decimal_places > maximum_places
                        ):
                            raise InvalidOperation
                    except InvalidOperation:
                        add_issue(
                            field,
                            "INVALID_AMOUNT",
                            "El importe no cumple formato, rango o escala del perfil.",
                        )

            for field, allowed_values in profile.enum_fields.items():
                if (
                    field not in invalid_length_fields
                    and vals[field]
                    and vals[field].upper() not in allowed_values
                ):
                    allowed = ", ".join(sorted(allowed_values))
                    add_issue(
                        field,
                        "INVALID_CURRENCY",
                        f"Valor no admitido por este perfil ({allowed}).",
                    )

            for field in profile.iso_date_fields:
                if field not in invalid_length_fields and vals[field]:
                    try:
                        if not DATE_PATTERN.fullmatch(vals[field]):
                            raise ValueError
                        date.fromisoformat(vals[field])
                    except ValueError:
                        add_issue(field, "INVALID_DATE", "Fecha obligatoria con formato AAAA-MM-DD y calendario válido.")

            if not row_issues:
                valid_rows += 1
            issues.extend(row_issues)
    except csv.Error as exc:
        raise InvalidDataset("CSV mal formado (comillas o delimitadores incorrectos).") from exc

    return total_rows, valid_rows, issues
