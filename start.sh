#!/bin/sh
python manage.py migrate --noinput  # Run migrations
exec gunicorn diagnosa_backend.wsgi:application --bind 0.0.0.0:8000  # Start Gunicorn
