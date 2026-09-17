# Partner CRM

Partner CRM is a Flask web application that displays partner contact details,
sales volumes, and automatically calculated discounts. The application uses
PostgreSQL for data storage and Bootstrap for the user interface.

## Install

Build and start the application with Docker Compose:

```bash
docker compose up --build
```

## Usage

Open Partner CRM in a browser:

```text
http://127.0.0.1:8000
```

## Development

Install the dependencies and run the application locally:

```bash
uv sync
docker compose up -d postgres
uv run python run.py
```

## Testing

Run the test suite:

```bash
docker compose up -d --wait postgres
uv run pytest
```
