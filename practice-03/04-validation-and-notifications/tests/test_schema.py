from pathlib import Path


SCHEMA = (Path(__file__).parents[1] / "database/01_schema_and_data.sql").read_text()


def test_partner_schema_matches_card_fields():
    partners_definition = SCHEMA.split("CREATE TABLE products")[0].lower()

    assert "inn" not in partners_definition
    assert "check (partner_type in ('ооо', 'зао', 'ип', 'тк'))" in partners_definition
    assert "address varchar(500) not null" in partners_definition
    assert "rating integer not null check (rating >= 0)" in partners_definition
    assert "email varchar(255) not null unique" in partners_definition


def test_sales_foreign_keys_and_seed_data_are_preserved():
    assert "references partners(id) on delete restrict" in SCHEMA.lower()
    assert "insert into sales_history" in SCHEMA.lower()
    assert "insert into products" in SCHEMA.lower()
