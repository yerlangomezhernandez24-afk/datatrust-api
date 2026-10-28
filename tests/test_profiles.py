import json

import pytest
from fastapi.testclient import TestClient

from datatrust_api.main import create_app
from datatrust_api.profiles import InvalidProfile, UnknownProfile, get_profile, parse_profile


HEAD = "order_id,customer_id,email,amount,currency,order_date\n"
EUR_ROW = "O1,C1,a@example.invalid,10,EUR,2026-10-25\n"


def valid_profile_document(**overrides):
    document = {
        "id": "test_v1",
        "version": 1,
        "description": "Perfil sintético para pruebas.",
        "max_rows": 100,
        "required_fields": ["id", "email", "amount", "kind", "date"],
        "identifier_fields": ["id"],
        "unique_fields": ["id"],
        "email_fields": ["email"],
        "positive_decimal_fields": ["amount"],
        "field_limits": {
            field: {"max_characters": 100, "max_utf8_bytes": 400}
            for field in ["id", "email", "amount", "kind", "date"]
        },
        "decimal_policies": {
            "amount": {
                "minimum": "0.01",
                "maximum": "9999.99",
                "currency_field": "kind",
                "max_decimal_places_by_currency": {"A": 2, "B": 2},
                "allow_scientific": False,
            }
        },
        "enum_fields": {"kind": ["A", "B"]},
        "iso_date_fields": ["date"],
    }
    document.update(overrides)
    return document


def test_profiles_endpoint_lists_only_local_allowed_profiles(tmp_path):
    with TestClient(create_app(str(tmp_path / "profiles.db"))) as client:
        response = client.get("/api/v1/profiles")

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": "orders_usd_v1",
            "version": 1,
            "description": "Pedidos con las mismas reglas base y moneda USD obligatoria.",
        },
        {
            "id": "orders_v1",
            "version": 1,
            "description": "Perfil base de pedidos con monedas CRC, USD o EUR.",
        },
    ]


def test_profile_selection_preserves_default_and_applies_usd_rule(tmp_path):
    with TestClient(create_app(str(tmp_path / "selection.db"))) as client:
        default_response = client.post(
            "/api/v1/runs",
            files={"file": ("orders.csv", HEAD + EUR_ROW, "text/csv")},
        )
        usd_response = client.post(
            "/api/v1/runs?profile=orders_usd_v1",
            files={"file": ("orders.csv", HEAD + EUR_ROW, "text/csv")},
        )
        usd_issues = client.get(
            f"/api/v1/runs/{usd_response.json()['id']}/issues"
        ).json()

    assert default_response.status_code == 201, default_response.text
    assert default_response.json()["profile"] == "orders_v1"
    assert default_response.json()["valid_rows"] == 1
    assert usd_response.status_code == 201, usd_response.text
    assert usd_response.json()["profile"] == "orders_usd_v1"
    assert usd_response.json()["valid_rows"] == 0
    assert [issue["code"] for issue in usd_issues] == ["INVALID_CURRENCY"]


def test_unknown_profile_is_rejected_without_persistence_or_path_access(tmp_path):
    with TestClient(create_app(str(tmp_path / "unknown.db"))) as client:
        response = client.post(
            "/api/v1/runs?profile=../../private.json",
            files={"file": ("orders.csv", HEAD + EUR_ROW, "text/csv")},
        )

        assert response.status_code == 422
        assert response.json()["detail"] == "Perfil no admitido."
        assert "../../private.json" not in response.text
        assert client.get("/api/v1/runs").json() == []

    with pytest.raises(UnknownProfile):
        get_profile("../../private.json")


@pytest.mark.parametrize(
    "document",
    [
        valid_profile_document(shell_command="echo unsafe"),
        valid_profile_document(unique_fields=["missing"]),
        valid_profile_document(required_fields=["id", "id"]),
        valid_profile_document(max_rows=0),
        valid_profile_document(enum_fields={"kind": []}),
    ],
)
def test_profile_json_schema_rejects_unknown_or_unsafe_configuration(document):
    with pytest.raises(InvalidProfile):
        parse_profile(json.dumps(document), expected_id="test_v1")


def test_profile_json_rejects_duplicate_object_keys():
    source = json.dumps(valid_profile_document()).replace(
        '"id": "test_v1"',
        '"id": "test_v1", "id": "shadowed_v1"',
        1,
    )

    with pytest.raises(InvalidProfile, match="repetida"):
        parse_profile(source, expected_id="test_v1")


@pytest.mark.parametrize(
    "case",
    ["missing_limit", "unknown_currency_scale", "scientific", "reversed_range"],
)
def test_profile_json_rejects_unsafe_field_or_decimal_policy(case):
    document = valid_profile_document()
    if case == "missing_limit":
        document["field_limits"].pop("email")
    elif case == "unknown_currency_scale":
        document["decimal_policies"]["amount"][
            "max_decimal_places_by_currency"
        ] = {"A": 2, "B": 2, "C": 2}
    elif case == "scientific":
        document["decimal_policies"]["amount"]["allow_scientific"] = True
    else:
        document["decimal_policies"]["amount"]["minimum"] = "10.00"
        document["decimal_policies"]["amount"]["maximum"] = "1.00"

    with pytest.raises(InvalidProfile):
        parse_profile(json.dumps(document), expected_id="test_v1")
