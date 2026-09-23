import pytest

from app.validation import ALLOWED_PARTNER_TYPES, validate_partner_form


def valid_form(**overrides):
    form = {
        "name": "Партнер",
        "partner_type": "ООО",
        "rating": "0",
        "address": "г. Москва, ул. Тестовая, д. 1",
        "director_name": "Иванов Иван Иванович",
        "phone": "+7 (999) 123-45-67",
        "email": "partner@example.com",
    }
    form.update(overrides)
    return form


def test_valid_form_is_trimmed_and_rating_is_integer():
    cleaned, errors = validate_partner_form(
        valid_form(name="  Партнер  ", email=" partner@example.com ", rating=" 0 ")
    )

    assert errors == {}
    assert cleaned["name"] == "Партнер"
    assert cleaned["email"] == "partner@example.com"
    assert cleaned["rating"] == 0


@pytest.mark.parametrize(
    ("rating", "expected"),
    [
        ("", "Укажите рейтинг"),
        ("   ", "Укажите рейтинг"),
        ("-1", "целым неотрицательным"),
        ("1.5", "целым неотрицательным"),
        ("abc", "целым неотрицательным"),
        ("2147483648", "2147483647"),
    ],
)
def test_invalid_ratings(rating, expected):
    _, errors = validate_partner_form(valid_form(rating=rating))

    assert expected in errors["rating"]


@pytest.mark.parametrize(
    "email",
    [
        "plain",
        "a@",
        "@example.com",
        "a@localhost",
        "a..b@example",
        "a@example..com",
        f"{'a' * 65}@example.com",
    ],
)
def test_invalid_emails(email):
    _, errors = validate_partner_form(valid_form(email=email))

    assert "формате name@example.com" in errors["email"]


@pytest.mark.parametrize(
    "phone",
    [
        "123456",
        "1234567890123456",
        "+7 999 CALL-NOW",
        "+7.999.123.45.67",
        "１２３４５６７８９",
    ],
)
def test_invalid_phones(phone):
    _, errors = validate_partner_form(valid_form(phone=phone))

    assert "+7 (999) 000-00-00" in errors["phone"]


def test_empty_phone_is_allowed():
    cleaned, errors = validate_partner_form(valid_form(phone="   "))

    assert errors == {}
    assert cleaned["phone"] == ""


@pytest.mark.parametrize("partner_type", ["АО", "ooo", "", " ОООО "])
def test_only_declared_partner_types_are_allowed(partner_type):
    _, errors = validate_partner_form(valid_form(partner_type=partner_type))

    assert "partner_type" in errors


@pytest.mark.parametrize("partner_type", ALLOWED_PARTNER_TYPES)
def test_each_declared_partner_type_is_valid(partner_type):
    _, errors = validate_partner_form(valid_form(partner_type=partner_type))

    assert errors == {}


@pytest.mark.parametrize(
    ("field", "length"),
    [
        ("name", 256),
        ("director_name", 256),
        ("email", 256),
        ("partner_type", 101),
        ("phone", 33),
        ("address", 501),
    ],
)
def test_max_lengths_are_guarded(field, length):
    _, errors = validate_partner_form(valid_form(**{field: "x" * length}))

    assert "Сократите значение" in errors[field]


@pytest.mark.parametrize(
    "field", ["name", "partner_type", "rating", "address", "director_name", "email"]
)
def test_all_database_required_fields_are_required(field):
    _, errors = validate_partner_form(valid_form(**{field: "  "}))

    assert field in errors
