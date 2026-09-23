import os

import psycopg2
from flask import Flask, abort, flash, redirect, render_template, request, url_for

from app.database import create_partner, get_partner, get_partners, update_partner
from app.validation import ALLOWED_PARTNER_TYPES, validate_partner_form


app = Flask(
    __name__,
    static_folder="app/static",
    template_folder="app/templates",
)
app.config.update(
    DATABASE_URL=os.getenv(
        "DATABASE_URL",
        "postgresql://postgres:postgres@localhost:5436/partner_crm",
    ),
    SECRET_KEY=os.getenv("SECRET_KEY", "development-only-change-me"),
)


def render_partner_form(*, mode, partner=None, errors=None, database_error=None, status=200):
    return render_template(
        "partner_form.html",
        mode=mode,
        partner=partner or {},
        errors=errors or {},
        database_error=database_error,
        partner_types=ALLOWED_PARTNER_TYPES,
    ), status


def database_error_message():
    return (
        "Не удалось сохранить данные. Проверьте доступность PostgreSQL и повторите попытку. "
        "Введенные значения сохранены в форме."
    )


@app.get("/")
def partner_list():
    try:
        partners = get_partners()
    except psycopg2.Error:
        return render_template(
            "partners.html",
            partners=[],
            database_error=(
                "Не удалось получить список партнеров. Проверьте подключение к PostgreSQL "
                "и повторите попытку."
            ),
        ), 503
    return render_template("partners.html", partners=partners, database_error=None)


@app.route("/partners/new", methods=["GET", "POST"])
def partner_create():
    if request.method == "GET":
        return render_partner_form(mode="create")

    posted = request.form.to_dict()
    cleaned, errors = validate_partner_form(request.form)
    if errors:
        return render_partner_form(
            mode="create", partner=posted, errors=errors, status=400
        )

    try:
        create_partner(cleaned)
    except psycopg2.errors.UniqueViolation:
        return render_partner_form(
            mode="create",
            partner=posted,
            errors={"email": "Этот email уже используется. Укажите другой адрес."},
            status=409,
        )
    except psycopg2.Error:
        return render_partner_form(
            mode="create",
            partner=posted,
            database_error=database_error_message(),
            status=503,
        )

    flash("Партнер успешно добавлен.", "information")
    return redirect(url_for("partner_list"))


@app.route("/partners/<int:partner_id>/edit", methods=["GET", "POST"])
def partner_edit(partner_id):
    try:
        partner = get_partner(partner_id)
    except psycopg2.Error:
        return render_partner_form(
            mode="edit",
            database_error=(
                "Не удалось загрузить данные партнера. Проверьте доступность PostgreSQL "
                "и повторите попытку."
            ),
            status=503,
        )
    if partner is None:
        abort(404, description=f"Партнер с ID {partner_id} не найден.")

    if request.method == "GET":
        return render_partner_form(mode="edit", partner=partner)

    posted = request.form.to_dict()
    cleaned, errors = validate_partner_form(request.form)
    if errors:
        return render_partner_form(
            mode="edit", partner=posted, errors=errors, status=400
        )

    try:
        updated = update_partner(partner_id, cleaned)
    except psycopg2.errors.UniqueViolation:
        return render_partner_form(
            mode="edit",
            partner=posted,
            errors={"email": "Этот email уже используется. Укажите другой адрес."},
            status=409,
        )
    except psycopg2.Error:
        return render_partner_form(
            mode="edit",
            partner=posted,
            database_error=database_error_message(),
            status=503,
        )

    if not updated:
        abort(404, description=f"Партнер с ID {partner_id} больше не существует.")
    flash("Данные партнера успешно обновлены.", "information")
    return redirect(url_for("partner_list"))


@app.errorhandler(404)
def partner_not_found(error):
    return render_template("404.html", message=error.description), 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8004)
