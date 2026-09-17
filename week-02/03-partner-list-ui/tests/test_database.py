from app.database import get_partner, get_partners


def test_get_partners_from_database():
    partners = {partner["name"]: partner for partner in get_partners()}

    assert partners["Логистик-Экспресс"]["discount"] == 5
    assert partners["Петров А.В."]["discount"] == 10
    assert partners["Быстрый Путь"]["discount"] == 15
    assert partners["Северный Склад"]["total_quantity"] == 0
    assert partners["Северный Склад"]["discount"] == 0


def test_get_specific_and_missing_partners():
    assert get_partner(1)["name"] == "Логистик-Экспресс"
    assert get_partner(999_999) is None
