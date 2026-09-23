import psycopg2
from flask import current_app
from psycopg2.extras import RealDictCursor

from app.discount import calculate_partner_discount


PARTNERS_QUERY = """
    SELECT
        p.id, p.partner_type, p.name, p.address, p.director_name,
        p.phone, p.email, p.rating,
        COALESCE(SUM(s.quantity), 0)::BIGINT AS total_quantity
    FROM partners AS p
    LEFT JOIN sales_history AS s ON s.partner_id = p.id
    GROUP BY p.id
    ORDER BY p.name
"""

PARTNER_QUERY = """
    SELECT
        p.id, p.partner_type, p.name, p.address, p.director_name,
        p.phone, p.email, p.rating,
        COALESCE(SUM(s.quantity), 0)::BIGINT AS total_quantity
    FROM partners AS p
    LEFT JOIN sales_history AS s ON s.partner_id = p.id
    WHERE p.id = %s
    GROUP BY p.id
"""

WRITABLE_COLUMNS = (
    "name",
    "partner_type",
    "rating",
    "address",
    "director_name",
    "phone",
    "email",
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


def get_partner(partner_id):
    connection = get_connection()
    try:
        with connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(PARTNER_QUERY, (partner_id,))
            partner = cursor.fetchone()
    finally:
        connection.close()
    return add_discount(dict(partner)) if partner is not None else None


def create_partner(partner):
    values = tuple(
        partner[column] or None if column == "phone" else partner[column]
        for column in WRITABLE_COLUMNS
    )
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
                values,
            )
            partner_id = cursor.fetchone()[0]
        connection.commit()
        return partner_id
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def update_partner(partner_id, partner):
    values = tuple(
        partner[column] or None if column == "phone" else partner[column]
        for column in WRITABLE_COLUMNS
    )
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
                (*values, partner_id),
            )
            updated = cursor.rowcount == 1
        connection.commit()
        return updated
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
