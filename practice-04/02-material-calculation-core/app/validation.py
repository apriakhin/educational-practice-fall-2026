import re
from collections.abc import Mapping


ALLOWED_PARTNER_TYPES = ("ООО", "ЗАО", "ИП", "ТК")
FIELD_LIMITS = {
    "name": 255,
    "partner_type": 100,
    "director_name": 255,
    "phone": 32,
    "email": 255,
    "address": 500,
}
REQUIRED_FIELDS = {
    "name": "Укажите наименование партнера.",
    "partner_type": "Выберите тип партнера.",
    "rating": "Укажите рейтинг целым неотрицательным числом.",
    "address": "Укажите адрес партнера.",
    "director_name": "Укажите ФИО директора.",
    "email": "Укажите электронную почту партнера.",
}
EMAIL_RE = re.compile(
    r"^[A-Za-z0-9.!#$%&'*+/=?^_`{|}~-]+@"
    r"(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?\.)+"
    r"[A-Za-z]{2,63}$"
)
PHONE_RE = re.compile(r"^\+7 \(\d{3}\) \d{3}-\d{2}-\d{2}$")


def validate_partner_form(form: Mapping[str, object]):
    """Normalize partner fields and return (cleaned values, field errors)."""
    fields = (*FIELD_LIMITS.keys(), "rating")
    cleaned = {
        field: str(form.get(field, "") or "").strip()
        for field in fields
    }
    errors = {}

    for field, message in REQUIRED_FIELDS.items():
        if not cleaned[field]:
            errors[field] = message

    for field, limit in FIELD_LIMITS.items():
        if len(cleaned[field]) > limit:
            errors[field] = (
                f"Сократите значение до {limit} символов или меньше."
            )

    if (
        cleaned["partner_type"]
        and "partner_type" not in errors
        and cleaned["partner_type"] not in ALLOWED_PARTNER_TYPES
    ):
        errors["partner_type"] = "Выберите тип партнера из списка: ООО, ЗАО, ИП или ТК."

    rating_text = cleaned["rating"]
    if rating_text:
        if not re.fullmatch(r"\d+", rating_text):
            errors["rating"] = "Введите рейтинг целым неотрицательным числом, например 0 или 5."
        else:
            rating = int(rating_text)
            if rating > 2_147_483_647:
                errors["rating"] = "Уменьшите рейтинг до 2147483647 или меньше."
            else:
                cleaned["rating"] = rating

    email = cleaned["email"]
    if email and len(email) <= FIELD_LIMITS["email"]:
        local_part = email.partition("@")[0]
        if (
            not EMAIL_RE.fullmatch(email)
            or len(local_part) > 64
            or local_part.startswith(".")
            or local_part.endswith(".")
            or ".." in email
        ):
            errors["email"] = "Исправьте email: укажите адрес в формате name@example.com."

    phone = cleaned["phone"]
    if phone and len(phone) <= FIELD_LIMITS["phone"]:
        if not PHONE_RE.fullmatch(phone):
            errors["phone"] = (
                "Исправьте телефон: укажите российский номер в формате "
                "+7 (999) 000-00-00."
            )

    return cleaned, errors
