#!/bin/sh

python manage.py makemigrations
python manage.py migrate
echo "copiando arquivos estáticos"
python manage.py collectstatic --noinput --clear > /dev/null
echo "copiando arquivos estáticos"
gunicorn electre_mor_project.wsgi:application --bind 0.0.0.0:8000

exec "$@"
