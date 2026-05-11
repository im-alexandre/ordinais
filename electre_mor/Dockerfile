FROM node:22-alpine AS frontend-builder

WORKDIR /usr/src/app

COPY ./frontend/package*.json ./frontend/
WORKDIR /usr/src/app/frontend
RUN npm ci

COPY ./frontend/ ./
RUN npm run build

FROM python:3.13-slim

WORKDIR /usr/src/app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN pip install --upgrade pip

COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
COPY --from=frontend-builder /usr/src/app/static/frontend ./static/frontend

RUN chmod +x ./entrypoint_electre.sh
RUN python manage.py collectstatic --noinput --clear
