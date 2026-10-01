from decimal import Decimal

import pytest

from app import materials


@pytest.fixture(autouse=True)
def reference_factors(monkeypatch):
    def lookup(product_type_id, material_type_id):
        products = {1: Decimal("1.00"), 2: Decimal("1.25")}
        materials = {1: Decimal("0"), 2: Decimal("5")}
        if product_type_id not in products or material_type_id not in materials:
            return None
        return {"coefficient": products[product_type_id], "defect_percent": materials[material_type_id]}

    monkeypatch.setattr(materials, "get_material_factors", lookup)


def test_standard_calculation():
    assert materials.calculate_materials(2, 2, 10, 2.0, 3.0) == 79


def test_fraction_is_rounded_up():
    assert materials.calculate_materials(1, 1, 1, 1.01, 1.0) == 2
    assert materials.calculate_materials(1, 1, 1, 2.0, 1.0) == 2


@pytest.mark.parametrize("product_id, material_id", [(999, 1), (1, 999)])
def test_unknown_type_returns_minus_one(product_id, material_id):
    assert materials.calculate_materials(product_id, material_id, 1, 1.0, 1.0) == -1


@pytest.mark.parametrize("param_1, param_2", [(-1.0, 1.0), (1.0, -2.0), (0.0, 1.0)])
def test_invalid_dimensions_return_minus_one(param_1, param_2):
    assert materials.calculate_materials(1, 1, 1, param_1, param_2) == -1


@pytest.mark.parametrize("quantity", [0, -1])
def test_nonpositive_quantity_returns_minus_one(quantity):
    assert materials.calculate_materials(1, 1, quantity, 1.0, 1.0) == -1


@pytest.mark.parametrize("value", [float('nan'), float('inf'), 'bad'])
def test_nonfinite_or_nonnumeric_dimension_returns_minus_one(value):
    assert materials.calculate_materials(1, 1, 1, value, 1.0) == -1
