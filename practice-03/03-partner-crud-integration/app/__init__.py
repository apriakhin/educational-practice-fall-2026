import os

import psycopg2
from flask import Flask, abort, redirect, render_template, request, url_for

from app.database import create_partner, get_partner, get_partners, update_partner


PARTNER_TYPES = ("ООО", "ЗАО", "ИП", "ТК")
FORM_FIELDS = (
    "name",
    "partner_type",
    "rating",
    "address",
    "director_name",
    "phone",
    "email",
)
REQUIRED_FIELDS = tuple(field for field in FORM_FIELDS if field != "phone")


def validate_partner_form(form):
    partner = {field: form.get(field, "").strip() for field in FORM_FIELDS}
    errors = []

    if any(not partner[field] for field in REQUIRED_FIELDS):
        errors.append("Заполните все обязательные поля.")
    if partner["partner_type"] and partner["partner_type"] not in PARTNER_TYPES:
        errors.append("Выберите тип партнера из списка.")

    try:
        partner["rating"] = int(partner["rating"])
        if partner["rating"] < 0:
            errors.append("Рейтинг должен быть целым неотрицательным числом.")
    except (TypeError, ValueError):
        errors.append("Рейтинг должен быть целым неотрицательным числом.")

    return partner, errors


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_mapping(
        DATABASE_URL=os.getenv(
            "DATABASE_URL",
            "postgresql://postgres:postgres@localhost:5435/partner_crm",
        )
    )
    if test_config:
        app.config.update(test_config)

    @app.get("/")
    def partner_list():
        try:
            partners = get_partners()
        except psycopg2.Error:
            return render_template("partners.html", partners=[], database_error=True), 503
        return render_template("partners.html", partners=partners, database_error=False)

    @app.route("/partners/new", methods=("GET", "POST"))
    def partner_new():
        partner = {field: "" for field in FORM_FIELDS}
        errors = []
        if request.method == "POST":
            partner, errors = validate_partner_form(request.form)
            if not errors:
                try:
                    create_partner(partner)
                except psycopg2.Error:
                    errors.append(
                        "Не удалось сохранить партнера. Проверьте уникальность email "
                        "и доступность базы данных."
                    )
                else:
                    return redirect(url_for("partner_list"))
        return render_template(
            "partner_form.html",
            page_title="CRM: Карточка партнера [Добавление]",
            heading="Добавление партнера",
            partner=partner,
            partner_types=PARTNER_TYPES,
            errors=errors,
        )

    @app.route("/partners/<int:partner_id>/edit", methods=("GET", "POST"))
    def partner_edit(partner_id):
        try:
            stored_partner = get_partner(partner_id)
        except psycopg2.Error:
            return render_template("database_error.html"), 503
        if stored_partner is None:
            abort(404, description=f"Партнер с ID {partner_id} не найден.")

        partner = stored_partner
        errors = []
        if request.method == "POST":
            partner, errors = validate_partner_form(request.form)
            if not errors:
                try:
                    updated = update_partner(partner_id, partner)
                except psycopg2.Error:
                    errors.append(
                        "Не удалось сохранить изменения. Проверьте уникальность email "
                        "и доступность базы данных."
                    )
                else:
                    if not updated:
                        abort(404, description=f"Партнер с ID {partner_id} не найден.")
                    return redirect(url_for("partner_list"))
        return render_template(
            "partner_form.html",
            page_title="CRM: Карточка партнера [Редактирование]",
            heading="Редактирование партнера",
            partner=partner,
            partner_types=PARTNER_TYPES,
            errors=errors,
        )

    @app.errorhandler(404)
    def not_found(error):
        return render_template("404.html", message=error.description), 404

    return app
