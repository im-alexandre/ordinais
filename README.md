# Ordinais / ELECTRE-MOr

Aplicacao Django 5.2 com API Django REST Framework e frontend React servido pelo proprio Django.

## Stack

- Python 3.13
- Django 5.2
- Django REST Framework 3.17
- PostgreSQL 14 em container
- React 19 + Vite

## Desenvolvimento

```powershell
cd D:\ordinais\electre_mor
python -m pip install -r requirements.txt
python manage.py check
python manage.py test
```

Frontend:

```powershell
cd D:\ordinais\electre_mor\frontend
npm install
npm run test
npm run build
```

Executar localmente:

```powershell
cd D:\ordinais\electre_mor
python manage.py migrate
python manage.py runserver 127.0.0.1:8000
```

- Interface: http://127.0.0.1:8000/
- API: http://127.0.0.1:8000/api/v1/projects/

## Docker

```powershell
cd D:\ordinais
docker compose build
docker compose up
```

O `docker-compose.yml` preserva os labels Traefik para Coolify.
