import pytest

from app import database


class FakeCursor:
    def __init__(self, *, one=None, all_rows=None, rowcount=1, failure=None):
        self.one = one
        self.all_rows = all_rows or []
        self.rowcount = rowcount
        self.failure = failure
        self.executions = []

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def execute(self, query, parameters=None):
        self.executions.append((query, parameters))
        if self.failure:
            raise self.failure

    def fetchone(self):
        return self.one

    def fetchall(self):
        return self.all_rows


class FakeConnection:
    def __init__(self, cursor):
        self.fake_cursor = cursor
        self.commits = 0
        self.rollbacks = 0
        self.closed = 0

    def cursor(self, **kwargs):
        return self.fake_cursor

    def commit(self):
        self.commits += 1

    def rollback(self):
        self.rollbacks += 1

    def close(self):
        self.closed += 1


PARTNER = {
    "name": "Партнер",
    "partner_type": "ООО",
    "rating": 0,
    "address": "Адрес",
    "director_name": "Директор",
    "phone": "",
    "email": "partner@example.com",
}


def test_create_is_parameterized_and_committed(monkeypatch):
    cursor = FakeCursor(one=(42,))
    connection = FakeConnection(cursor)
    monkeypatch.setattr(database, "get_connection", lambda: connection)

    assert database.create_partner(PARTNER) == 42

    query, parameters = cursor.executions[0]
    assert "VALUES (%s, %s, %s, %s, %s, %s, %s)" in query
    assert parameters[2] == 0
    assert parameters[-2] is None
    assert "Партнер" not in query
    assert connection.commits == 1
    assert connection.rollbacks == 0
    assert connection.closed == 1


def test_update_is_parameterized_and_keeps_partner_id(monkeypatch):
    cursor = FakeCursor(rowcount=1)
    connection = FakeConnection(cursor)
    monkeypatch.setattr(database, "get_connection", lambda: connection)

    assert database.update_partner(9, PARTNER) is True

    query, parameters = cursor.executions[0]
    assert "WHERE id = %s" in query
    assert parameters[-1] == 9
    assert connection.commits == 1


def test_write_failure_rolls_back_and_closes(monkeypatch):
    cursor = FakeCursor(failure=RuntimeError("write failed"))
    connection = FakeConnection(cursor)
    monkeypatch.setattr(database, "get_connection", lambda: connection)

    with pytest.raises(RuntimeError, match="write failed"):
        database.create_partner(PARTNER)

    assert connection.commits == 0
    assert connection.rollbacks == 1
    assert connection.closed == 1


def test_get_partner_is_parameterized(monkeypatch):
    cursor = FakeCursor(one={"id": 5, **PARTNER})
    connection = FakeConnection(cursor)
    monkeypatch.setattr(database, "get_connection", lambda: connection)

    result = database.get_partner(5)

    assert result["id"] == 5
    assert cursor.executions[0][1] == (5,)
    assert connection.closed == 1


def test_get_partners_adds_discount(monkeypatch):
    row = {"id": 1, **PARTNER, "total_quantity": 50_000}
    cursor = FakeCursor(all_rows=[row])
    connection = FakeConnection(cursor)
    monkeypatch.setattr(database, "get_connection", lambda: connection)

    partners = database.get_partners()

    assert partners[0]["discount"] == 10
    assert connection.closed == 1
