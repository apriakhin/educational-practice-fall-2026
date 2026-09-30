# Partner Sales History

This project adds a sales history page to the partner CRM. A button on each
partner card opens a table of products, quantities, and sale dates.

## Install

Build and start the application with Docker Compose:

```bash
docker compose up --build
```

## Usage

Open the partner registry in a browser:

```text
http://127.0.0.1:8005
```

## Development

Install the dependencies and run the application locally:

```bash
uv sync
docker compose up -d postgres
uv run python run.py
```

The application reads two environment variables:

- `DATABASE_URL`, defaults to `postgresql://postgres:postgres@localhost:5437/partner_crm`;
- `SECRET_KEY`, used for flash messages; set a random value in production.

## Testing

Run the test suite:

```bash
uv run pytest
```
