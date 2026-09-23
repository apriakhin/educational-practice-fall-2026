# Partner Validation and Notifications

This project adds server-side validation and interactive MessageBox dialogs to
the partner CRM. Errors, unsaved change warnings, and success notifications are
shown in Bootstrap modal windows. The application uses PostgreSQL for data
storage and Bootstrap for the user interface.

## Install

Build and start the application with Docker Compose:

```bash
docker compose up --build
```

## Usage

Open the partner registry in a browser:

```text
http://127.0.0.1:8004
```

## Development

Install the dependencies and run the application locally:

```bash
uv sync
docker compose up -d postgres
uv run python run.py
```

The application reads two environment variables:

- `DATABASE_URL`, defaults to `postgresql://postgres:postgres@localhost:5436/partner_crm`;
- `SECRET_KEY`, used for flash messages; set a random value in production.

## Testing

Run the test suite:

```bash
uv run pytest
```
