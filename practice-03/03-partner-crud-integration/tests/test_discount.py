import pytest

from app.discount import calculate_partner_discount


@pytest.mark.parametrize(
    ("quantity", "discount"),
    [(0, 0), (9_999, 0), (10_000, 5), (50_000, 10), (300_000, 15)],
)
def test_discount_boundaries(quantity, discount):
    assert calculate_partner_discount(quantity) == discount


def test_discount_rejects_negative_quantity():
    with pytest.raises(ValueError):
        calculate_partner_discount(-1)
