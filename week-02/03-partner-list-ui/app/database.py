import os

import psycopg2
from psycopg2.extras import RealDictCursor

from app.discount import calculate_partner_discount


DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/partner_crm",
)

PARTNERS_QUERY = """
    SELECT
        partners.id,
        partners.partner_type,
        partners.name,
        partners.director_name,
        partners.phone,
        partners.email,
        partners.rating,
        COALESCE(SUM(sales_history.quantity), 0)::BIGINT AS total_quantity
    FROM partners
    LEFT JOIN sales_history ON sales_history.partner_id = partners.id
    GROUP BY partners.id
    ORDER BY partners.name
"""

PARTNER_QUERY = """
    SELECT
        partners.id,
        partners.partner_type,
        partners.name,
        partners.director_name,
        partners.phone,
        partners.email,
        partners.rating,
        COALESCE(SUM(sales_history.quantity), 0)::BIGINT AS total_quantity
    FROM partners
    LEFT JOIN sales_history ON sales_history.partner_id = partners.id
    WHERE partners.id = %s
    GROUP BY partners.id
"""


def get_connection():
    return psycopg2.connect(DATABASE_URL, connect_timeout=5)


def add_discount(partner):
    partner["discount"] = calculate_partner_discount(partner["total_quantity"])
    return partner


def get_partners():
    connection = get_connection()
    try:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(PARTNERS_QUERY)
            partners = cursor.fetchall()
    finally:
        connection.close()
    return [add_discount(dict(partner)) for partner in partners]


def get_partner(partner_id: int):
    connection = get_connection()
    try:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(PARTNER_QUERY, (partner_id,))
            partner = cursor.fetchone()
    finally:
        connection.close()
    if partner is None:
        return None
    return add_discount(dict(partner))
