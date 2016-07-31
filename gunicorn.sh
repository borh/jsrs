#!/bin/sh
python manage.py collectstatic --noinput
gunicorn config.wsgi:application -w 4 -b 0.0.0.0:8000 --reload --timeout 60 --log-level debug
