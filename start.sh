#!/bin/sh
python manage.py migrate --noinput  # Run migrations
gunicorn diagnosa_backend.wsgi:application --bind 0.0.0.0:8000  # Start Gunicorn