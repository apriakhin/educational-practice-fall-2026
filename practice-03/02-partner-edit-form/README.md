# Partner Edit Form

This project adds a partner card form to the CRM. The form contains every
partner field and shows hints for the expected phone and email format, but it
does not save data to the database yet. The application uses PostgreSQL for data
storage and Bootstrap for the user interface.

## Install

Build and start the application with Docker Compose:

```bash
docker compose up --build
```

## Usage

Open the partner card form in a browser:

```text
http://127.0.0.1:8002/partners/new
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
uv run pytest
```
