import pytest

from app.discount import calculate_partner_discount


@pytest.mark.parametrize(
    ("total_quantity", "expected_discount"),
    [
        (0, 0),
        (9_999, 0),
        (10_000, 5),
        (49_999, 5),
        (50_000, 10),
        (299_999, 10),
        (300_000, 15),
    ],
)
def test_calculate_partner_discount_boundaries(total_quantity, expected_discount):
    assert calculate_partner_discount(total_quantity) == expected_discount


def test_calculate_partner_discount_rejects_negative_quantity():
    with pytest.raises(ValueError, match="cannot be negative"):
        calculate_partner_discount(-1)
