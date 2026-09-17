from app.database import add_discount, get_partner, get_partners


def test_add_discount_to_partner_dictionary():
    partner = {"name": "Test Partner", "total_quantity": 50_000}

    result = add_discount(partner)

    assert result["discount"] == 10


def test_add_discount_handles_null_total_quantity():
    result = add_discount({"name": "Partner without sales", "total_quantity": None})

    assert result["total_quantity"] == 0
    assert result["discount"] == 0


def test_get_partners_from_database():
    partners = {partner["name"]: partner for partner in get_partners()}

    assert partners["Логистик-Экспресс"]["total_quantity"] == 10_000
    assert partners["Логистик-Экспресс"]["discount"] == 5
    assert partners["Петров А.В."]["total_quantity"] == 50_000
    assert partners["Петров А.В."]["discount"] == 10
    assert partners["Быстрый Путь"]["total_quantity"] == 300_000
    assert partners["Быстрый Путь"]["discount"] == 15
    assert partners["Северный Склад"]["total_quantity"] == 0
    assert partners["Северный Склад"]["discount"] == 0


def test_get_specific_partner_from_database():
    partner = get_partner(1)

    assert partner["name"] == "Логистик-Экспресс"
    assert partner["discount"] == 5


def test_get_missing_partner_from_database():
    assert get_partner(999_999) is None
