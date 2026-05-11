#!/bin/sh

python manage.py migrate --noinput
exec gunicorn electre_mor_project.wsgi:application --bind 0.0.0.0:80
