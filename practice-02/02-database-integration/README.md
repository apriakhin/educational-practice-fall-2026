# Partner Database Integration

This project loads partner sales totals from PostgreSQL and adds the calculated
discount percentage to each partner dictionary.

## Install

```bash
uv sync
```

## Database

```bash
docker compose up -d
```

## Usage

```bash
uv run python main.py
```

## Testing

```bash
docker compose up -d --wait postgres
uv run pytest
```

## Stop

```bash
docker compose down
```
