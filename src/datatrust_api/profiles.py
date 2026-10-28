"""Perfiles JSON locales, versionados y validados mediante una lista permitida."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from functools import lru_cache
from importlib.resources import files
from types import MappingProxyType
from typing import Mapping

PROFILE_FILES = {
    "orders_v1": "orders_v1.json",
    "orders_usd_v1": "orders_usd_v1.json",
}
PROFILE_KEYS = {
    "id",
    "version",
    "description",
    "max_rows",
    "required_fields",
    "identifier_fields",
    "unique_fields",
    "email_fields",
    "positive_decimal_fields",
    "field_limits",
    "decimal_policies",
    "enum_fields",
    "iso_date_fields",
}
PROFILE_ID_PATTERN = re.compile(r"^[a-z][a-z0-9_]*_v([1-9][0-9]*)$")
FIELD_PATTERN = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")


class InvalidProfile(ValueError):
    """El JSON local no cumple el esquema estricto permitido."""


class UnknownProfile(LookupError):
    """El identificador no pertenece al registro local permitido."""


@dataclass(frozen=True)
class FieldLimit:
    max_characters: int
    max_utf8_bytes: int


@dataclass(frozen=True)
class DecimalPolicy:
    minimum: Decimal
    maximum: Decimal
    currency_field: str
    max_decimal_places_by_currency: Mapping[str, int]
    allow_scientific: bool


@dataclass(frozen=True)
class ValidationProfile:
    id: str
    version: int
    description: str
    max_rows: int
    required_fields: tuple[str, ...]
    identifier_fields: tuple[str, ...]
    unique_fields: tuple[str, ...]
    email_fields: tuple[str, ...]
    positive_decimal_fields: tuple[str, ...]
    field_limits: Mapping[str, FieldLimit]
    decimal_policies: Mapping[str, DecimalPolicy]
    enum_fields: Mapping[str, frozenset[str]]
    iso_date_fields: tuple[str, ...]

    def summary(self) -> dict:
        return {
            "id": self.id,
            "version": self.version,
            "description": self.description,
        }


def _string_list(document: dict, key: str, *, allow_empty: bool = True) -> tuple[str, ...]:
    value = document[key]
    if not isinstance(value, list) or not all(
        isinstance(item, str) and FIELD_PATTERN.fullmatch(item) for item in value
    ):
        raise InvalidProfile(f"{key} debe ser una lista de nombres de campo válidos.")
    if not allow_empty and not value:
        raise InvalidProfile(f"{key} no puede estar vacío.")
    if len(value) != len(set(value)):
        raise InvalidProfile(f"{key} contiene campos repetidos.")
    return tuple(value)


def _object_without_duplicate_keys(pairs: list[tuple[str, object]]) -> dict:
    document = {}
    for key, value in pairs:
        if key in document:
            raise InvalidProfile(f"El objeto JSON contiene la clave repetida: {key}.")
        document[key] = value
    return document


def _parse_field_limits(document: dict, required: set[str]) -> Mapping[str, FieldLimit]:
    limits_document = document["field_limits"]
    if not isinstance(limits_document, dict) or set(limits_document) != required:
        raise InvalidProfile("field_limits debe definir exactamente los campos obligatorios.")
    limits: dict[str, FieldLimit] = {}
    for field, value in limits_document.items():
        if not isinstance(value, dict) or set(value) != {
            "max_characters",
            "max_utf8_bytes",
        }:
            raise InvalidProfile("Cada límite debe definir caracteres y bytes UTF-8.")
        max_characters = value["max_characters"]
        max_utf8_bytes = value["max_utf8_bytes"]
        if (
            type(max_characters) is not int
            or type(max_utf8_bytes) is not int
            or not 1 <= max_characters <= 100_000
            or not max_characters <= max_utf8_bytes <= 2 * 1024 * 1024
        ):
            raise InvalidProfile("Los límites de campo no son enteros seguros y coherentes.")
        limits[field] = FieldLimit(max_characters, max_utf8_bytes)
    return MappingProxyType(limits)


def _parse_decimal_policies(
    document: dict,
    decimal_fields: tuple[str, ...],
    required: set[str],
    enum_fields: Mapping[str, frozenset[str]],
) -> Mapping[str, DecimalPolicy]:
    policies_document = document["decimal_policies"]
    if not isinstance(policies_document, dict) or set(policies_document) != set(
        decimal_fields
    ):
        raise InvalidProfile(
            "decimal_policies debe definir exactamente los campos decimales."
        )
    policies: dict[str, DecimalPolicy] = {}
    for field, value in policies_document.items():
        if not isinstance(value, dict) or set(value) != {
            "minimum",
            "maximum",
            "currency_field",
            "max_decimal_places_by_currency",
            "allow_scientific",
        }:
            raise InvalidProfile("La política decimal contiene claves inválidas.")
        minimum_text = value["minimum"]
        maximum_text = value["maximum"]
        if not all(
            isinstance(item, str) and re.fullmatch(r"[0-9]+(?:\.[0-9]+)?", item)
            for item in (minimum_text, maximum_text)
        ):
            raise InvalidProfile("Los rangos decimales deben usar texto decimal simple.")
        try:
            minimum = Decimal(minimum_text)
            maximum = Decimal(maximum_text)
        except InvalidOperation as exc:
            raise InvalidProfile("El rango decimal no es válido.") from exc
        if not minimum.is_finite() or not maximum.is_finite() or minimum <= 0 or maximum < minimum:
            raise InvalidProfile("El rango decimal debe ser finito, positivo y ordenado.")
        currency_field = value["currency_field"]
        if (
            not isinstance(currency_field, str)
            or currency_field not in required
            or currency_field not in enum_fields
        ):
            raise InvalidProfile("La política decimal debe referir una enumeración de moneda.")
        places_document = value["max_decimal_places_by_currency"]
        if (
            not isinstance(places_document, dict)
            or set(places_document) != set(enum_fields[currency_field])
            or not all(type(places) is int and 0 <= places <= 18 for places in places_document.values())
        ):
            raise InvalidProfile("La escala debe cubrir las monedas permitidas con enteros entre 0 y 18.")
        if value["allow_scientific"] is not False:
            raise InvalidProfile("Esta versión solo admite allow_scientific=false.")
        policies[field] = DecimalPolicy(
            minimum=minimum,
            maximum=maximum,
            currency_field=currency_field,
            max_decimal_places_by_currency=MappingProxyType(dict(places_document)),
            allow_scientific=False,
        )
    return MappingProxyType(policies)


def parse_profile(source: str, *, expected_id: str) -> ValidationProfile:
    try:
        document = json.loads(source, object_pairs_hook=_object_without_duplicate_keys)
    except json.JSONDecodeError as exc:
        raise InvalidProfile("El perfil no contiene JSON válido.") from exc
    if not isinstance(document, dict):
        raise InvalidProfile("La raíz del perfil debe ser un objeto JSON.")
    if set(document) != PROFILE_KEYS:
        missing = sorted(PROFILE_KEYS - set(document))
        unknown = sorted(set(document) - PROFILE_KEYS)
        raise InvalidProfile(
            f"Claves de perfil inválidas; faltantes={missing}, desconocidas={unknown}."
        )

    profile_id = document["id"]
    if not isinstance(profile_id, str) or profile_id != expected_id:
        raise InvalidProfile("El id del perfil no coincide con el registro permitido.")
    match = PROFILE_ID_PATTERN.fullmatch(profile_id)
    if match is None:
        raise InvalidProfile("El id del perfil debe ser local y versionado, por ejemplo orders_v1.")
    version = document["version"]
    if type(version) is not int or version <= 0 or version != int(match.group(1)):
        raise InvalidProfile("La versión debe ser un entero positivo coherente con el id.")
    description = document["description"]
    if not isinstance(description, str) or not description.strip() or len(description) > 200:
        raise InvalidProfile("La descripción debe contener entre 1 y 200 caracteres.")
    max_rows = document["max_rows"]
    if type(max_rows) is not int or not 1 <= max_rows <= 10_000:
        raise InvalidProfile("max_rows debe ser un entero entre 1 y 10000.")

    required_fields = _string_list(document, "required_fields", allow_empty=False)
    identifier_fields = _string_list(document, "identifier_fields")
    unique_fields = _string_list(document, "unique_fields")
    email_fields = _string_list(document, "email_fields")
    positive_decimal_fields = _string_list(document, "positive_decimal_fields")
    iso_date_fields = _string_list(document, "iso_date_fields")
    required = set(required_fields)
    referenced = {
        *unique_fields,
        *identifier_fields,
        *email_fields,
        *positive_decimal_fields,
        *iso_date_fields,
    }

    enum_document = document["enum_fields"]
    if not isinstance(enum_document, dict):
        raise InvalidProfile("enum_fields debe ser un objeto campo -> valores permitidos.")
    enum_fields: dict[str, frozenset[str]] = {}
    for field, choices in enum_document.items():
        if not isinstance(field, str) or FIELD_PATTERN.fullmatch(field) is None:
            raise InvalidProfile("enum_fields contiene un nombre de campo inválido.")
        if (
            not isinstance(choices, list)
            or not choices
            or not all(isinstance(choice, str) and choice for choice in choices)
            or len(choices) != len(set(choices))
        ):
            raise InvalidProfile("Cada enumeración debe contener valores de texto únicos.")
        enum_fields[field] = frozenset(choices)
        referenced.add(field)

    if not referenced <= required:
        raise InvalidProfile("Todas las reglas deben referirse a campos obligatorios.")

    field_limits = _parse_field_limits(document, required)
    decimal_policies = _parse_decimal_policies(
        document,
        positive_decimal_fields,
        required,
        enum_fields,
    )

    return ValidationProfile(
        id=profile_id,
        version=version,
        description=description.strip(),
        max_rows=max_rows,
        required_fields=required_fields,
        identifier_fields=identifier_fields,
        unique_fields=unique_fields,
        email_fields=email_fields,
        positive_decimal_fields=positive_decimal_fields,
        field_limits=field_limits,
        decimal_policies=decimal_policies,
        enum_fields=MappingProxyType(enum_fields),
        iso_date_fields=iso_date_fields,
    )


@lru_cache(maxsize=len(PROFILE_FILES))
def get_profile(profile_id: str) -> ValidationProfile:
    filename = PROFILE_FILES.get(profile_id)
    if filename is None:
        raise UnknownProfile("Perfil no admitido.")
    source = (
        files("datatrust_api")
        .joinpath("profile_data", filename)
        .read_text(encoding="utf-8")
    )
    return parse_profile(source, expected_id=profile_id)


def list_profiles() -> list[ValidationProfile]:
    return [get_profile(profile_id) for profile_id in sorted(PROFILE_FILES)]
