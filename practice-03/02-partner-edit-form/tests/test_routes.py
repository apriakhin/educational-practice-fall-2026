import psycopg2

from run import app


def test_partner_list_title_content_and_navigation(monkeypatch):
    partner = {
        "partner_type": "ООО",
        "name": "Тестовый партнер",
        "address": "г. Москва, ул. Тестовая, д. 1",
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
    assert "<title>CRM: Реестр партнеров</title>" in response.text
    assert "Тестовый партнер" in response.text
    assert "г. Москва, ул. Тестовая, д. 1" in response.text
    assert 'href="/partners/new"' in response.text
    assert "Добавить партнера" in response.text


def test_partner_form_has_title_navigation_and_all_fields():
    response = app.test_client().get("/partners/new")

    assert response.status_code == 200
    assert "<title>CRM: Карточка партнера [Добавление]</title>" in response.text
    for field_name in (
        "name",
        "partner_type",
        "rating",
        "address",
        "director_name",
        "phone",
        "email",
    ):
        assert f'name="{field_name}"' in response.text
    assert 'href="/"' in response.text
    assert "Реестр партнеров" in response.text
    assert "Сохранить" in response.text
    assert "Назад" in response.text


def test_partner_form_select_and_rating_constraints():
    response = app.test_client().get("/partners/new")

    assert '<select class="form-select" id="partner_type" name="partner_type" required>' in response.text
    for partner_type in ("ООО", "ЗАО", "ИП", "ТК"):
        assert f'value="{partner_type}"' in response.text
    assert 'type="number" min="0" step="1"' in response.text
    assert "Целое неотрицательное число" in response.text


def test_partner_form_contact_placeholders_titles_and_hints():
    response = app.test_client().get("/partners/new")

    assert 'placeholder="+7 (999) 000-00-00"' in response.text
    assert 'title="Введите телефон в формате +7 (999) 000-00-00"' in response.text
    assert "Ожидаемый формат: +7 (999) 000-00-00" in response.text
    assert "data-phone-mask" in response.text
    assert "phone-mask.js" in response.text
    assert 'placeholder="partner@example.com"' in response.text
    assert 'title="Введите email в формате partner@example.com"' in response.text
    assert "Ожидаемый формат: partner@example.com" in response.text


def test_partner_form_post_redisplays_values_without_saving():
    response = app.test_client().post(
        "/partners/new",
        data={
            "name": "Новый партнер",
            "partner_type": "ЗАО",
            "rating": "7",
            "address": "г. Казань, ул. Новая, д. 10",
            "director_name": "Сидоров Петр Иванович",
            "phone": "+7 999 123-45-67",
            "email": "new@example.com",
        },
    )

    assert response.status_code == 200
    assert "Сохранение в базе данных в этом задании не выполняется" in response.text
    assert 'value="Новый партнер"' in response.text
    assert 'value="ЗАО" selected' in response.text
    assert "г. Казань, ул. Новая, д. 10" in response.text


def test_partner_list_handles_database_error(monkeypatch):
    def raise_database_error():
        raise psycopg2.OperationalError("database unavailable")

    monkeypatch.setattr("run.get_partners", raise_database_error)

    response = app.test_client().get("/")

    assert response.status_code == 503
    assert "Ошибка подключения" in response.text


def test_local_static_resources_are_available():
    client = app.test_client()

    assert client.get("/static/resources/logo.svg").status_code == 200
    assert client.get("/static/resources/favicon.svg").status_code == 200
    assert client.get("/static/phone-mask.js").status_code == 200
