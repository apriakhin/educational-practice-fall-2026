from flask import current_app
import psycopg2
from psycopg2.extras import RealDictCursor

from app.discount import calculate_partner_discount


PARTNERS_QUERY = """
    SELECT
        partners.id,
        partners.partner_type,
        partners.name,
        partners.address,
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
    SELECT id, partner_type, name, rating, address, director_name, phone, email
    FROM partners
    WHERE id = %s
"""

PARTNER_FIELDS = (
    "name",
    "partner_type",
    "rating",
    "address",
    "director_name",
    "phone",
    "email",
)


def partner_parameters(partner):
    return tuple(
        None if field == "phone" and not partner[field] else partner[field]
        for field in PARTNER_FIELDS
    )


def get_connection():
    return psycopg2.connect(current_app.config["DATABASE_URL"], connect_timeout=5)


def add_discount(partner):
    partner["total_quantity"] = partner["total_quantity"] or 0
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
    return dict(partner) if partner is not None else None


def create_partner(partner):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO partners
                    (name, partner_type, rating, address, director_name, phone, email)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id
                """,
                partner_parameters(partner),
            )
            partner_id = cursor.fetchone()[0]
        connection.commit()
        return partner_id
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def update_partner(partner_id: int, partner):
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                """
                UPDATE partners
                SET name = %s,
                    partner_type = %s,
                    rating = %s,
                    address = %s,
                    director_name = %s,
                    phone = %s,
                    email = %s
                WHERE id = %s
                """,
                partner_parameters(partner) + (partner_id,),
            )
            updated = cursor.rowcount > 0
        connection.commit()
        return updated
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
