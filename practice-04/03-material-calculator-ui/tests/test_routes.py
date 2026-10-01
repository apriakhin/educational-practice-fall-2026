import psycopg2
import pytest
from datetime import date

import run


VALID_FORM = {
    "name": "Новый партнер",
    "partner_type": "ЗАО",
    "rating": "7",
    "address": "г. Москва, ул. Новая, д. 5",
    "director_name": "Петров Петр Петрович",
    "phone": "+7 (999) 000-00-00",
    "email": "new@example.com",
}

PARTNER = {
    "id": 12,
    "name": "Тестовый партнер",
    "partner_type": "ООО",
    "rating": 5,
    "address": "Тестовый адрес",
    "director_name": "Иванов Иван Иванович",
    "phone": None,
    "email": "test@example.com",
}


@pytest.fixture(autouse=True)
def configure_app():
    run.app.config.update(TESTING=True, SECRET_KEY="test-secret")


def test_registry_title_cards_and_click_to_edit(monkeypatch):
    listed = {**PARTNER, "discount": 10, "total_quantity": 50_000}
    monkeypatch.setattr(run, "get_partners", lambda: [listed])

    response = run.app.test_client().get("/")

    assert response.status_code == 200
    assert "<title>CRM: Реестр партнеров</title>" in response.text
    assert "/partners/12/edit" in response.text
    assert "stretched-link" in response.text
    assert "Тестовый партнер" in response.text
    assert "Тестовый адрес" in response.text


def test_registry_database_failure_is_503_error_message_box(monkeypatch):
    def fail():
        raise psycopg2.OperationalError("secret database details")

    monkeypatch.setattr(run, "get_partners", fail)
    response = run.app.test_client().get("/")

    assert response.status_code == 503
    assert 'id="errorMessageBox"' in response.text
    assert "Ошибка" in response.text
    assert "icon-error" in response.text
    assert "secret database details" not in response.text


def test_new_form_has_exact_title_fields_hints_and_dirty_hooks():
    response = run.app.test_client().get("/partners/new")

    assert response.status_code == 200
    assert "<title>CRM: Карточка партнера [Добавление]</title>" in response.text
    for field in VALID_FORM:
        assert f'name="{field}"' in response.text
    assert response.text.count("placeholder=") >= 6
    assert response.text.count('data-bs-toggle="tooltip"') >= 7
    assert 'id="warningMessageBox"' in response.text
    assert "icon-warning" in response.text
    assert "partner-form.js" in response.text
    assert "data-phone-mask" in response.text
    assert 'placeholder="+7 (999) 000-00-00"' in response.text


def test_edit_loads_current_data_and_has_exact_title(monkeypatch):
    monkeypatch.setattr(run, "get_partner", lambda partner_id: PARTNER)

    response = run.app.test_client().get("/partners/12/edit")

    assert response.status_code == 200
    assert "<title>CRM: Карточка партнера [Редактирование]</title>" in response.text
    assert 'value="Тестовый партнер"' in response.text
    assert 'value="test@example.com"' in response.text


def test_missing_edit_is_404(monkeypatch):
    monkeypatch.setattr(run, "get_partner", lambda partner_id: None)

    response = run.app.test_client().get("/partners/999/edit")

    assert response.status_code == 404
    assert "CRM: Партнер не найден" in response.text
    assert 'id="errorMessageBox"' in response.text
    assert "Партнер с ID 999 не найден" in response.text


def test_create_uses_clean_values_and_prg_information(monkeypatch):
    captured = {}

    def create(data):
        captured.update(data)
        return 12

    monkeypatch.setattr(run, "create_partner", create)
    monkeypatch.setattr(run, "get_partners", lambda: [])
    client = run.app.test_client()

    response = client.post(
        "/partners/new",
        data={**VALID_FORM, "name": "  Новый партнер  ", "rating": "0"},
    )

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")
    assert captured["name"] == "Новый партнер"
    assert captured["rating"] == 0

    redirected = client.get(response.headers["Location"])
    assert 'id="informationMessageBox"' in redirected.text
    assert "Партнер успешно добавлен" in redirected.text
    assert "icon-information" in redirected.text


def test_update_uses_prg(monkeypatch):
    captured = {}
    monkeypatch.setattr(run, "get_partner", lambda partner_id: PARTNER)
    monkeypatch.setattr(
        run, "update_partner", lambda partner_id, data: captured.update(data) is None
    )

    response = run.app.test_client().post("/partners/12/edit", data=VALID_FORM)

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")
    assert captured["email"] == "new@example.com"


def test_update_missing_partner_is_404(monkeypatch):
    monkeypatch.setattr(run, "get_partner", lambda partner_id: PARTNER)
    monkeypatch.setattr(run, "update_partner", lambda partner_id, data: False)

    response = run.app.test_client().post("/partners/404/edit", data=VALID_FORM)

    assert response.status_code == 404


def test_validation_preserves_posted_values_and_shows_error_modal(monkeypatch):
    monkeypatch.setattr(run, "create_partner", lambda data: pytest.fail("must not write"))
    posted = {**VALID_FORM, "name": "  Оставить пробелы  ", "rating": "1.5"}

    response = run.app.test_client().post("/partners/new", data=posted)

    assert response.status_code == 400
    assert 'value="  Оставить пробелы  "' in response.text
    assert 'value="1.5"' in response.text
    assert 'id="errorMessageBox"' in response.text
    assert "Исправьте указанные поля" in response.text


def test_unique_email_has_tailored_message(monkeypatch):
    def duplicate(data):
        raise psycopg2.errors.UniqueViolation()

    monkeypatch.setattr(run, "create_partner", duplicate)
    response = run.app.test_client().post("/partners/new", data=VALID_FORM)

    assert response.status_code == 409
    assert "Этот email уже используется" in response.text
    assert 'value="new@example.com"' in response.text


def test_write_database_failure_is_safe_503_and_preserves_data(monkeypatch):
    def fail(data):
        raise psycopg2.DatabaseError("password=do-not-leak")

    monkeypatch.setattr(run, "create_partner", fail)
    response = run.app.test_client().post("/partners/new", data=VALID_FORM)

    assert response.status_code == 503
    assert "Не удалось сохранить данные" in response.text
    assert 'value="Новый партнер"' in response.text
    assert "password=do-not-leak" not in response.text


def test_local_static_resources_are_available():
    client = run.app.test_client()

    for path in ("logo.svg", "favicon.svg"):
        assert client.get(f"/static/resources/{path}").status_code == 200
    assert client.get("/static/js/partner-form.js").status_code == 200


def test_history_link_and_sales_page(monkeypatch):
    monkeypatch.setattr(run, "get_partners", lambda: [{**PARTNER, "discount": 0, "total_quantity": 3}])
    monkeypatch.setattr(run, "get_partner", lambda partner_id: PARTNER)
    monkeypatch.setattr(run, "get_sales_history", lambda partner_id: [{"product_name": "Мыло", "quantity": 3, "sale_date": date(2026, 3, 1)}])
    client = run.app.test_client()

    assert '/partners/12/history' in client.get('/').text
    response = client.get('/partners/12/history')
    assert response.status_code == 200
    assert '<title>CRM: История реализации продукции — Тестовый партнер</title>' in response.text
    assert 'Мыло' in response.text
    assert '01.03.2026' in response.text


def test_history_missing_partner_is_404(monkeypatch):
    monkeypatch.setattr(run, "get_partner", lambda partner_id: None)
    assert run.app.test_client().get('/partners/999/history').status_code == 404


def test_calculator_shows_result_and_handles_invalid_input(monkeypatch):
    monkeypatch.setattr(run, "calculate_materials", lambda *args: 13 if args[3] > 0 else -1)
    client = run.app.test_client()
    form = {"product_type_id": "1", "material_type_id": "2", "quantity": "10", "param_1": "1", "param_2": "1"}

    assert 'Калькулятор материалов' in client.get('/materials/calculator').text
    assert 'Необходимое количество материала' in client.post('/materials/calculator', data=form).text
    assert 'Расчет невозможен' in client.post('/materials/calculator', data={**form, 'param_1': '-1'}).text
    assert 'Введите корректные числовые значения' in client.post('/materials/calculator', data={**form, 'quantity': 'abc'}).text
