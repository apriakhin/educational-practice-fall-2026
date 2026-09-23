import pytest

from app import database


class FakeCursor:
    def __init__(self, *, fetchone=(42,), rowcount=1):
        self.fetchone_result = fetchone
        self.rowcount = rowcount
        self.query = None
        self.params = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return False

    def execute(self, query, params=None):
        self.query = query
        self.params = params

    def fetchone(self):
        return self.fetchone_result


class FakeConnection:
    def __init__(self, cursor):
        self.cursor_instance = cursor
        self.committed = False
        self.rolled_back = False
        self.closed = False

    def cursor(self, **_kwargs):
        return self.cursor_instance

    def commit(self):
        self.committed = True

    def rollback(self):
        self.rolled_back = True

    def close(self):
        self.closed = True


@pytest.fixture
def partner_data():
    return {
        "name": "Mock Partner",
        "partner_type": "ООО",
        "rating": 4,
        "address": "Mock address",
        "director_name": "Mock Director",
        "phone": "+70000000000",
        "email": "mock@example.com",
    }


def test_create_partner_uses_parameters_and_commits(monkeypatch, partner_data):
    cursor = FakeCursor(fetchone=(123,))
    connection = FakeConnection(cursor)
    monkeypatch.setattr(database, "get_connection", lambda: connection)

    partner_id = database.create_partner(partner_data)

    assert partner_id == 123
    assert cursor.params == tuple(
        partner_data[column] for column in database.WRITABLE_COLUMNS
    )
    assert "%s" in cursor.query
    assert partner_data["name"] not in cursor.query
    assert connection.committed
    assert connection.closed


def test_update_partner_does_not_change_id_or_history(monkeypatch, partner_data):
    cursor = FakeCursor(rowcount=1)
    connection = FakeConnection(cursor)
    monkeypatch.setattr(database, "get_connection", lambda: connection)

    updated = database.update_partner(7, partner_data)

    assert updated is True
    assert cursor.params[-1] == 7
    assert "WHERE id = %s" in cursor.query
    assert "sales_history" not in cursor.query
    assert "SET id" not in cursor.query
    assert connection.committed


def test_update_returns_false_when_partner_is_missing(monkeypatch, partner_data):
    connection = FakeConnection(FakeCursor(rowcount=0))
    monkeypatch.setattr(database, "get_connection", lambda: connection)

    assert database.update_partner(999, partner_data) is False
    assert connection.committed


def test_create_converts_empty_optional_phone_to_null(monkeypatch, partner_data):
    cursor = FakeCursor()
    connection = FakeConnection(cursor)
    monkeypatch.setattr(database, "get_connection", lambda: connection)
    partner_data["phone"] = ""

    database.create_partner(partner_data)

    assert cursor.params[database.WRITABLE_COLUMNS.index("phone")] is None


def test_write_rolls_back_and_closes_on_error(monkeypatch, partner_data):
    class BrokenCursor(FakeCursor):
        def execute(self, query, params=None):
            raise RuntimeError("write failed")

    connection = FakeConnection(BrokenCursor())
    monkeypatch.setattr(database, "get_connection", lambda: connection)

    with pytest.raises(RuntimeError, match="write failed"):
        database.create_partner(partner_data)

    assert connection.rolled_back
    assert connection.closed
