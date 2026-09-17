import psycopg2

from run import app


def test_partner_list_renders_content(monkeypatch):
    partner = {
        "partner_type": "ООО",
        "name": "Тестовый партнер",
        "director_name": "Иванов Иван Иванович",
        "phone": "+79990000000",
        "email": "partner@example.com",
        "rating": 5,
        "discount": 10,
        "total_quantity": 50_000,
    }
    monkeypatch.setattr("run.get_partners", lambda: [partner])
    app.config["TESTING"] = True

    response = app.test_client().get("/")

    assert response.status_code == 200
    assert "Partner CRM" in response.text
    assert "Тестовый партнер" in response.text
    assert "bootstrap@5.3.8" in response.text
    assert "/static/resources/logo.svg" in response.text
    assert "/static/resources/favicon.svg" in response.text
    assert "bootstrap-icons" not in response.text


def test_partner_list_handles_missing_contact_data(monkeypatch):
    partner = {
        "partner_type": "ООО",
        "name": "Партнер без контактов",
        "director_name": "Иванов Иван Иванович",
        "phone": None,
        "email": None,
        "rating": None,
        "discount": 0,
        "total_quantity": 0,
    }
    monkeypatch.setattr("run.get_partners", lambda: [partner])

    response = app.test_client().get("/")

    assert response.status_code == 200
    assert response.text.count("Не указан") == 3
    assert "0%" in response.text


def test_partner_list_renders_empty_state(monkeypatch):
    monkeypatch.setattr("run.get_partners", lambda: [])

    response = app.test_client().get("/")

    assert response.status_code == 200
    assert "Партнеры пока не добавлены" in response.text


def test_partner_list_handles_database_error(monkeypatch):
    def raise_database_error():
        raise psycopg2.OperationalError("database unavailable")

    monkeypatch.setattr("run.get_partners", raise_database_error)

    response = app.test_client().get("/")

    assert response.status_code == 503
    assert "Ошибка подключения" in response.text


def test_local_brand_resources_are_available():
    client = app.test_client()

    assert client.get("/static/resources/logo.svg").status_code == 200
    assert client.get("/static/resources/favicon.svg").status_code == 200
