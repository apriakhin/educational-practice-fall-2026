import os

import pytest

from app import create_app
from app.database import add_discount, get_partners


def test_add_discount_handles_null_total_quantity():
    result = add_discount({"name": "Partner without sales", "total_quantity": None})

    assert result["total_quantity"] == 0
    assert result["discount"] == 0


@pytest.mark.skipif(not os.getenv("DATABASE_URL"), reason="DATABASE_URL is not set")
def test_seeded_partners_and_discounts():
    app = create_app({"DATABASE_URL": os.environ["DATABASE_URL"]})

    with app.app_context():
        partners = {partner["name"]: partner for partner in get_partners()}

    assert partners["Логистик-Экспресс"]["discount"] == 5
    assert partners["Петров А.В."]["discount"] == 10
    assert partners["Быстрый Путь"]["discount"] == 15
    assert partners["Северный Склад"]["discount"] == 0
    assert all(partner["address"] for partner in partners.values())
