# Partner CRUD Integration

This project connects the partner card form to PostgreSQL. It supports creating
and editing partners, loads the current data into the form, and refreshes the
registry after saving. The application uses PostgreSQL for data storage and
Bootstrap for the user interface.

## Install

Build and start the application with Docker Compose:

```bash
docker compose up --build
```

## Usage

Open the partner registry in a browser:

```text
http://127.0.0.1:8003
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
