#!/bin/sh
set -e

# Ensure deps are synced inside the container (dev-friendly)
if [ -f uv.lock ]; then
  uv sync --frozen --no-dev
else
  uv sync --no-dev
fi

uv run python manage.py migrate --noinput
uv run python manage.py collectstatic --noinput

# Execute the command passed to the container
exec "$@"