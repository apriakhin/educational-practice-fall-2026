import run
from run import app


def test_partner_list_renders_demo_content():
    app.config["TESTING"] = True

    response = app.test_client().get("/")

    assert response.status_code == 200
    assert "Partner CRM" in response.text
    assert "Логистик-Экспресс" in response.text
    assert "bootstrap@5.3.8" in response.text
    assert "/static/resources/logo.svg" in response.text
    assert "/static/resources/favicon.svg" in response.text
    assert "bootstrap-icons" not in response.text


def test_partner_list_renders_empty_state(monkeypatch):
    monkeypatch.setattr(run, "DEMO_PARTNERS", [])

    response = app.test_client().get("/")

    assert response.status_code == 200
    assert "Партнеры пока не добавлены" in response.text


def test_local_brand_resources_are_available():
    client = app.test_client()

    assert client.get("/static/resources/logo.svg").status_code == 200
    assert client.get("/static/resources/favicon.svg").status_code == 200
