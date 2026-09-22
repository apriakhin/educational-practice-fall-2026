import os

import psycopg2
from flask import Flask, render_template, request

from app.database import get_partners


app = Flask(
    __name__,
    static_folder="app/static",
    template_folder="app/templates",
)
app.config["DATABASE_URL"] = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5434/partner_crm",
)

PARTNER_TYPES = ("ООО", "ЗАО", "ИП", "ТК")


@app.get("/")
def partner_list():
    try:
        partners = get_partners()
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


@app.route("/partners/new", methods=["GET", "POST"])
def partner_new():
    return render_template(
        "partner_form.html",
        partner_types=PARTNER_TYPES,
        form=request.form,
        submitted=request.method == "POST",
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8002)
