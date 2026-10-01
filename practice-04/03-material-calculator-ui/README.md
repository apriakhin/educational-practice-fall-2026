# Material Calculator

This project adds a material calculator to the partner CRM. The calculator
displays the required material quantity or an input error on the form. It uses
`app.materials.calculate_materials(product_type_id, material_type_id, quantity, param_1, param_2)`
to read coefficients and defect rates from PostgreSQL and round the result up.

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
http://127.0.0.1:8007
```

## Development

Install the dependencies and run the application locally:

```bash
uv sync
docker compose up -d postgres
uv run python run.py
```

The application reads two environment variables:

- `DATABASE_URL`, defaults to `postgresql://postgres:postgres@localhost:5439/partner_crm`;
- `SECRET_KEY`, used for flash messages; set a random value in production.

## Testing

Run the test suite:

```bash
uv run pytest
```
