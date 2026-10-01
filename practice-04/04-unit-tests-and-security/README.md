# Material Calculator Tests and Security

This project adds unit tests for material calculations and checks that SQL
queries use parameters. Application errors are logged with timestamps in the
container console (`docker compose logs web`).

Sample data: product type 1 has coefficient 1.00, type 2 has 1.25;
material type 1 has a 0% defect rate, type 2 has 5%.

## Install

Build and start the application with Docker Compose:

```bash
docker compose up --build
```

## Usage

Open the partner registry in a browser:

```text
http://127.0.0.1:8008
```

## Development

Install the dependencies and run the application locally:

```bash
uv sync
docker compose up -d postgres
uv run python run.py
```

The application reads two environment variables:

- `DATABASE_URL`, defaults to `postgresql://postgres:postgres@localhost:5440/partner_crm`;
- `SECRET_KEY`, used for flash messages; set a random value in production.

## Testing

Run the test suite:

```bash
uv run pytest
```
