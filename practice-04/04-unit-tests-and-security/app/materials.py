import logging
import math
from decimal import Decimal, InvalidOperation, ROUND_CEILING

from app.database import get_material_factors


def calculate_materials(product_type_id: int, material_type_id: int,
                        quantity: int, param_1: float, param_2: float) -> int:
    """Return required material units rounded up, or -1 for invalid input."""
    if any(type(value) is not int or value <= 0 for value in
           (product_type_id, material_type_id, quantity)):
        return -1
    try:
        if any(not math.isfinite(float(value)) or float(value) <= 0 for value in
               (param_1, param_2)):
            return -1
        size_1 = Decimal(str(param_1))
        size_2 = Decimal(str(param_2))
        factors = get_material_factors(product_type_id, material_type_id)
        if factors is None:
            return -1
        coefficient = Decimal(str(factors["coefficient"]))
        defect_percent = Decimal(str(factors["defect_percent"]))
        if coefficient <= 0 or defect_percent < 0:
            return -1
        required = size_1 * size_2 * coefficient * quantity
        required *= 1 + defect_percent / 100
        return int(required.to_integral_value(rounding=ROUND_CEILING))
    except (ValueError, TypeError, OverflowError, InvalidOperation):
        return -1
    except Exception:
        logging.getLogger(__name__).exception("Ошибка получения коэффициентов для расчета материалов")
        return -1
