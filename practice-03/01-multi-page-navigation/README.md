# Partner Multi-Page Navigation

This project turns the partner CRM into a two-page Flask application. The main
page shows the partner registry, and the second page is prepared for the partner
card. Each page has its own title and navigation links. The application uses
PostgreSQL for data storage and Bootstrap for the user interface.

## Install

Build and start the application with Docker Compose:

```bash
docker compose up --build
```

## Usage

Open the partner registry in a browser:

```text
http://127.0.0.1:8001
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
