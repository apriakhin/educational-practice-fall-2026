from flask import Flask, render_template


app = Flask(
    __name__,
    static_folder="app/static",
    template_folder="app/templates",
)

DEMO_PARTNERS = [
    {
        "partner_type": "ООО",
        "name": "Логистик-Экспресс",
        "director_name": "Иванов Илья Сергеевич",
        "phone": "+79991112233",
        "email": "info@logex.ru",
        "rating": 4.8,
        "discount": 5,
        "total_quantity": 10_000,
    },
    {
        "partner_type": "ИП",
        "name": "Петров А.В.",
        "director_name": "Петров Алексей Викторович",
        "phone": None,
        "email": "petrov_delivery@mail.ru",
        "rating": 4.2,
        "discount": 10,
        "total_quantity": 50_000,
    },
]


@app.get("/")
def partner_list():
    return render_template(
        "partners.html",
        partners=DEMO_PARTNERS,
        database_error=False,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
