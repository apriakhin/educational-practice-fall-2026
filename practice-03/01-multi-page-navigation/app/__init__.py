import os

import psycopg2
from flask import Flask, render_template

from app import database


def create_app(test_config=None):
    app = Flask(__name__)
    app.config.from_mapping(
        DATABASE_URL=os.getenv(
            "DATABASE_URL",
            "postgresql://postgres:postgres@localhost:5433/partner_crm",
        )
    )
    if test_config:
        app.config.update(test_config)

    @app.get("/")
    def partner_list():
        try:
            partners = database.get_partners()
        except psycopg2.Error:
            return render_template(
                "partners.html",
                partners=[],
                database_error=True,
            ), 503
        return render_template(
            "partners.html",
            partners=partners,
            database_error=False,
        )

    @app.get("/partners/new")
    def partner_create():
        return render_template("partner_form.html")

    return app
