FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

WORKDIR /app

COPY pyproject.toml ./
RUN uv sync --no-dev --no-install-project

COPY app ./app
COPY run.py ./run.py

EXPOSE 8004

CMD ["uv", "run", "--no-dev", "python", "run.py"]
