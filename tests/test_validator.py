import pytest

from datatrust_api.validator import InvalidDataset, validate_orders_csv

HEAD = "order_id,customer_id,email,amount,currency,order_date\n"


def row(order_id="O1", customer="C1", email="ana@example.org", amount="19.99", currency="CRC", date="2026-10-25"):
    return f"{order_id},{customer},{email},{amount},{currency},{date}\n"


def test_valid_row():
    assert validate_orders_csv((HEAD + row()).encode()) == (1, 1, [])


def test_empty_dataset_with_header_is_accepted():
    assert validate_orders_csv(HEAD.encode()) == (0, 0, [])


def test_duplicate_ids_case_insensitive():
    total, valid, errors = validate_orders_csv((HEAD + row() + row(order_id="o1")).encode())
    assert (total, valid) == (2, 1)
    assert [i["code"] for i in errors] == ["DUPLICATE"]
    assert errors[0]["row_number"] == 3


@pytest.mark.parametrize("test_value,expected_code,field", [
    (row(order_id=""), "REQUIRED", "order_id"),
    (row(email="no-es-email"), "INVALID_EMAIL", "email"),
    (row(amount="-1"), "INVALID_AMOUNT", "amount"),
    (row(amount="NaN"), "INVALID_AMOUNT", "amount"),
    (row(currency="XXX"), "INVALID_CURRENCY", "currency"),
    (row(date="2026-02-30"), "INVALID_DATE", "order_date"),
    (row(date="20261025"), "INVALID_DATE", "order_date"),
])
def test_bad_values(test_value, expected_code, field):
    _, valid, errors = validate_orders_csv((HEAD + test_value).encode())
    assert valid == 0
    assert any(i["code"] == expected_code and i["field_name"] == field for i in errors)


def test_missing_headers_error():
    with pytest.raises(InvalidDataset, match="Faltan columnas"):
        validate_orders_csv(b"order_id,amount\nA1,2\n")


def test_duplicate_headers_error():
    with pytest.raises(InvalidDataset, match="repetidas"):
        validate_orders_csv((HEAD.rstrip("\n") + ",order_id\n").encode())


def test_mismatched_columns_flagged():
    _, _, issues = validate_orders_csv((HEAD + "O1,C1,x@example.org,9,CRC\n").encode())
    assert any(i["code"] == "COLUMN_COUNT" for i in issues)


def test_utf8_bom_supported():
    total, valid, errors = validate_orders_csv((HEAD + row()).encode("utf-8-sig"))
    assert (total, valid, errors) == (1, 1, [])


def test_invalid_utf8_rejected():
    with pytest.raises(InvalidDataset, match="UTF-8"):
        validate_orders_csv(b"\xff\xfe")


def test_unclosed_quotes_rejected():
    with pytest.raises(InvalidDataset, match="CSV mal formado"):
        validate_orders_csv((HEAD + '"bad,C1,x@a.io,2,USD,2026-10-25').encode())
