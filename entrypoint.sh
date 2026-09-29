#!/bin/sh
set -e

umask 022

uid="$(id -u)"

install -d /app/staticfiles /app/media

if [ "$uid" -eq 0 ]; then
    chown -R appuser:appgroup /app/staticfiles /app/media 2>/dev/null || true
fi

run_as_app() {
    if [ "$uid" -eq 0 ]; then
        gosu appuser "$@"
    else
        "$@"
    fi
}

if [ "$RUN_MIGRATIONS" = "true" ]; then
    echo "Running migrations..."
    run_as_app python manage.py migrate --noinput
fi

if [ "$RUN_COLLECTSTATIC" = "true" ]; then
    echo "Collecting static files..."
    run_as_app python manage.py collectstatic --noinput
fi

if [ "$uid" -eq 0 ]; then
    if [ "$RUN_COLLECTSTATIC" = "true" ]; then
        find /app/staticfiles -type d -exec chmod 755 {} \; 2>/dev/null || true
        find /app/staticfiles -type f -exec chmod 644 {} \; 2>/dev/null || true
    fi
    exec gosu appuser "$@"
fi

exec "$@"
