import pytest

from app import create_app


@pytest.fixture
def app():
    return create_app({"TESTING": True, "DATABASE_URL": "postgresql://unused"})


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def partner():
    return {
        "id": 7,
        "name": "Тестовый партнер",
        "partner_type": "ООО",
        "rating": 8,
        "address": "г. Москва, ул. Тестовая, д. 1",
        "director_name": "Иванов Иван Иванович",
        "phone": "+79990000000",
        "email": "partner@example.com",
        "discount": 10,
        "total_quantity": 50_000,
    }
