import csv
import os
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP


def normalize_phone(phone):
    phone = "".join(char for char in phone if char.isdigit())
    if phone.startswith("8"):
        phone = "7" + phone[1:]
    if len(phone) == 10:
        phone = "7" + phone
    if phone:
        phone = "+" + phone
    return phone


def normalize_date(sale_date):
    if "." in sale_date:
        return datetime.strptime(sale_date, "%d.%m.%Y").strftime("%Y-%m-%d")
    return sale_date


def write_csv(filename, fields, rows):
    with open(os.path.join(output_folder, filename), "w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


folder = os.path.dirname(__file__)
output_folder = os.path.join(folder, "normalized")
os.makedirs(output_folder, exist_ok=True)

with open(os.path.join(folder, "import_partners.csv"), encoding="utf-8") as file:
    partners_import = list(csv.DictReader(file))

partners = []
partner_ids = set()
for row in partners_import:
    partners.append({
        "id": row["partner_id"].strip(),
        "name": row["company_name"].strip(),
        "inn": row["inn"].strip(),
        "email": row["contact_email"].strip(),
        "phone": normalize_phone(row["phone"]),
    })
    partner_ids.add(row["partner_id"].strip())

with open(os.path.join(folder, "import_sales.txt"), encoding="utf-8") as file:
    sales_import = csv.DictReader(file, delimiter="\t")
    sales = [row for row in sales_import if row["partner_id"].strip() in partner_ids]

products = []
product_ids = {}
deliveries = []
for row in sales:
    product_name = row["product_name"].strip()
    quantity = int(row["quantity"])
    price = (Decimal(row["total_amount"]) / quantity).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )

    if product_name not in product_ids:
        product_id = len(product_ids) + 1
        product_ids[product_name] = product_id
        products.append({
            "id": product_id,
            "name": product_name,
            "sku": f"PRODUCT-{product_id:03d}",
            "price": price,
        })

    deliveries.append({
        "id": row["sale_id"].strip(),
        "partner_id": row["partner_id"].strip(),
        "product_id": product_ids[product_name],
        "quantity": quantity,
        "delivery_date": normalize_date(row["sale_date"].strip()),
    })

write_csv("partners.csv", ["id", "name", "inn", "email", "phone"], partners)
write_csv("products.csv", ["id", "name", "sku", "price"], products)
write_csv("deliveries.csv", ["id", "partner_id", "product_id", "quantity", "delivery_date"], deliveries)
