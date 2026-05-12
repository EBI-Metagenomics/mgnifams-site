FROM python:3.12-slim
LABEL authors="sandyr"

WORKDIR /app
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY mgnifams_site .

RUN mkdir -p /tmp/mgnifams_cache && chmod 777 /tmp/mgnifams_cache

EXPOSE 8000
ENV DJANGO_SETTINGS_MODULE=mgnifams_site.settings
ENV PYTHONUNBUFFERED=0

RUN .venv/bin/python manage.py collectstatic --noinput
CMD .venv/bin/gunicorn mgnifams_site.wsgi:application --bind 0.0.0.0:8000 --workers 3
