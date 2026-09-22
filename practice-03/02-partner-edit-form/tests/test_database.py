import os

import pytest

from app.database import PARTNERS_QUERY, PARTNER_QUERY, add_discount, get_partner, get_partners
from run import app


TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")


def test_queries_include_address_and_not_inn():
    assert "partners.address" in PARTNERS_QUERY
    assert "partners.address" in PARTNER_QUERY
    assert "inn" not in PARTNERS_QUERY.lower()
    assert "inn" not in PARTNER_QUERY.lower()


def test_add_discount_handles_null_total_quantity():
    result = add_discount({"name": "Partner without sales", "total_quantity": None})

    assert result["total_quantity"] == 0
    assert result["discount"] == 0


@pytest.mark.skipif(not TEST_DATABASE_URL, reason="TEST_DATABASE_URL is not set")
def test_get_partners_from_database():
    app.config["DATABASE_URL"] = TEST_DATABASE_URL
    with app.app_context():
        partners = {partner["name"]: partner for partner in get_partners()}

    assert partners["Логистик-Экспресс"]["address"] == "г. Москва, ул. Складская, д. 12"
    assert partners["Логистик-Экспресс"]["discount"] == 5
    assert partners["Петров А.В."]["discount"] == 10
    assert partners["Быстрый Путь"]["discount"] == 15
    assert partners["Северный Склад"]["rating"] == 4


@pytest.mark.skipif(not TEST_DATABASE_URL, reason="TEST_DATABASE_URL is not set")
def test_get_specific_and_missing_partners():
    app.config["DATABASE_URL"] = TEST_DATABASE_URL
    with app.app_context():
        partner = get_partner(1)
        missing_partner = get_partner(999_999)

    assert partner["name"] == "Логистик-Экспресс"
    assert partner["address"] == "г. Москва, ул. Складская, д. 12"
    assert missing_partner is None
