#!/bin/sh
poetry install --without dev
python manage.py migrate
exec gunicorn --bind 0.0.0.0:8000 app.wsgi:application --timeout 180