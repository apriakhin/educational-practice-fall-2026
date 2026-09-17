# Partner List UI

This project adds a responsive Flask and Bootstrap interface for displaying
partner cards. The page uses demonstration data before the final database
integration step.

## Install

```bash
uv sync
```

## Run

```bash
uv run python run.py
```

## Usage

```text
http://127.0.0.1:8000
```

## Testing

```bash
docker compose up -d --wait postgres
uv run pytest
```
