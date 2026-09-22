import psycopg2
import pytest

from app import create_app, database


@pytest.fixture
def client():
    return create_app({"TESTING": True}).test_client()


def test_partner_list_renders_partners_and_navigation(client, monkeypatch):
    partner = {
        "partner_type": "ООО",
        "name": "Тестовый партнер",
        "director_name": "Иванов Иван Иванович",
        "address": "г. Москва, ул. Тестовая, д. 1",
        "phone": "+79990000000",
        "email": "partner@example.com",
        "rating": 5,
        "discount": 10,
        "total_quantity": 50_000,
    }
    monkeypatch.setattr(database, "get_partners", lambda: [partner])

    response = client.get("/")

    assert response.status_code == 200
    assert "<title>CRM: Реестр партнеров</title>" in response.text
    assert "Тестовый партнер" in response.text
    assert "г. Москва, ул. Тестовая, д. 1" in response.text
    assert 'href="/partners/new"' in response.text
    assert "Добавить партнера" in response.text
    assert "bootstrap@5.3.8" in response.text


def test_partner_list_handles_database_error(client, monkeypatch):
    def raise_database_error():
        raise psycopg2.OperationalError("database unavailable")

    monkeypatch.setattr(database, "get_partners", raise_database_error)

    response = client.get("/")

    assert response.status_code == 503
    assert "Ошибка подключения" in response.text


def test_new_partner_page(client):
    response = client.get("/partners/new")

    assert response.status_code == 200
    assert "<title>CRM: Карточка партнера [Добавление]</title>" in response.text
    assert 'href="/"' in response.text
    assert "Назад" in response.text
    assert "<form" not in response.text


def test_static_resources_are_available(client):
    assert client.get("/static/resources/logo.svg").status_code == 200
    assert client.get("/static/resources/favicon.svg").status_code == 200
