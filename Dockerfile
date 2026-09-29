FROM python:3.12-slim-bookworm AS deps

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_LINK_MODE=copy \
    UV_PROJECT_ENVIRONMENT=/app/.venv

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY pyproject.toml uv.lock* ./

RUN uv sync --frozen --no-dev --no-install-project

FROM python:3.12-slim-bookworm AS app

ARG APP_UID=1000
ARG APP_GID=1000

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:${PATH}"

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    gosu \
    libpq5 \
    dos2unix \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN groupadd -g ${APP_GID} appgroup \
    && useradd -m -u ${APP_UID} -g appgroup appuser \
    && install -d -o appuser -g appgroup /app/staticfiles /app/media

COPY --from=deps /app/.venv /app/.venv

COPY --chown=appuser:appgroup . .

RUN dos2unix /app/entrypoint.sh \
    && chmod +x /app/entrypoint.sh

EXPOSE 8000
ENTRYPOINT ["/app/entrypoint.sh"]
