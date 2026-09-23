import psycopg2


def valid_form(**changes):
    data = {
        "name": "Новый партнер",
        "partner_type": "ЗАО",
        "rating": "5",
        "address": "г. Казань, ул. Новая, д. 5",
        "director_name": "Петров Петр Петрович",
        "phone": "+79991112233",
        "email": "new@example.com",
    }
    data.update(changes)
    return data


def test_registry_renders_cards_with_edit_links(client, monkeypatch, partner):
    monkeypatch.setattr("app.get_partners", lambda: [partner])

    response = client.get("/")

    assert response.status_code == 200
    assert "<title>CRM: Реестр партнеров</title>" in response.text
    assert "Тестовый партнер" in response.text
    assert 'href="/partners/7/edit"' in response.text
    assert "/partners/new" in response.text


def test_registry_handles_database_error(client, monkeypatch):
    def fail():
        raise psycopg2.OperationalError("unavailable")

    monkeypatch.setattr("app.get_partners", fail)

    response = client.get("/")

    assert response.status_code == 503
    assert "Ошибка подключения" in response.text


def test_new_get_renders_empty_form(client):
    response = client.get("/partners/new")

    assert response.status_code == 200
    assert "<title>CRM: Карточка партнера [Добавление]</title>" in response.text
    assert 'name="partner_type"' in response.text
    assert "ООО" in response.text
    assert "ЗАО" in response.text
    assert "ИП" in response.text
    assert "ТК" in response.text
    assert 'placeholder="+7 (999) 000-00-00"' in response.text
    assert "data-phone-mask" in response.text
    assert "phone-mask.js" in response.text


def test_new_post_creates_partner_and_redirects(client, monkeypatch):
    captured = {}

    def fake_create(partner):
        captured.update(partner)
        return 10

    monkeypatch.setattr("app.create_partner", fake_create)

    response = client.post("/partners/new", data=valid_form())

    assert response.status_code == 302
    assert response.headers["Location"] == "/"
    assert captured["rating"] == 5
    assert captured["email"] == "new@example.com"


def test_new_post_rejects_invalid_type_and_rating(client, monkeypatch):
    def should_not_run(_partner):
        raise AssertionError("create_partner must not be called")

    monkeypatch.setattr("app.create_partner", should_not_run)

    response = client.post(
        "/partners/new", data=valid_form(partner_type="АО", rating="-1")
    )

    assert response.status_code == 200
    assert "Выберите тип партнера из списка" in response.text
    assert "Рейтинг должен быть целым неотрицательным числом" in response.text


def test_new_post_accepts_empty_optional_phone(client, monkeypatch):
    captured = {}
    monkeypatch.setattr("app.create_partner", lambda partner: captured.update(partner) or 10)

    response = client.post("/partners/new", data=valid_form(phone=""))

    assert response.status_code == 302
    assert captured["phone"] == ""


def test_new_post_shows_database_error(client, monkeypatch):
    def fail(_partner):
        raise psycopg2.IntegrityError("duplicate email")

    monkeypatch.setattr("app.create_partner", fail)

    response = client.post("/partners/new", data=valid_form())

    assert response.status_code == 200
    assert "Проверьте уникальность email" in response.text
    assert "Новый партнер" in response.text


def test_edit_get_loads_current_partner(client, monkeypatch, partner):
    monkeypatch.setattr("app.get_partner", lambda partner_id: partner)

    response = client.get("/partners/7/edit")

    assert response.status_code == 200
    assert "<title>CRM: Карточка партнера [Редактирование]</title>" in response.text
    assert 'value="Тестовый партнер"' in response.text
    assert 'value="partner@example.com"' in response.text


def test_edit_post_updates_partner_and_redirects(client, monkeypatch, partner):
    captured = {}
    monkeypatch.setattr("app.get_partner", lambda partner_id: partner)

    def fake_update(partner_id, data):
        captured["id"] = partner_id
        captured["data"] = data
        return True

    monkeypatch.setattr("app.update_partner", fake_update)

    response = client.post("/partners/7/edit", data=valid_form(name="Изменен"))

    assert response.status_code == 302
    assert response.headers["Location"] == "/"
    assert captured["id"] == 7
    assert captured["data"]["name"] == "Изменен"


def test_edit_returns_clear_404_for_unknown_id(client, monkeypatch):
    monkeypatch.setattr("app.get_partner", lambda partner_id: None)

    response = client.get("/partners/999/edit")

    assert response.status_code == 404
    assert "Партнер с ID 999 не найден" in response.text


def test_edit_checks_rowcount_after_concurrent_removal(client, monkeypatch, partner):
    monkeypatch.setattr("app.get_partner", lambda partner_id: partner)
    monkeypatch.setattr("app.update_partner", lambda partner_id, data: False)

    response = client.post("/partners/7/edit", data=valid_form())

    assert response.status_code == 404
    assert "Партнер с ID 7 не найден" in response.text
