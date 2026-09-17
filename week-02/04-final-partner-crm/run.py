import os

import psycopg2
from flask import Flask, render_template

from app.database import get_partners


app = Flask(
    __name__,
    static_folder="app/static",
    template_folder="app/templates",
)
app.config["DATABASE_URL"] = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@localhost:5432/partner_crm",
)


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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
