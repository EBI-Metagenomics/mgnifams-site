FROM python:3.12-slim
LABEL authors="sandyr"

WORKDIR /app
COPY mgnifams_site .
COPY requirements.txt .

RUN pip install -r requirements.txt

RUN mkdir -p /tmp/mgnifams_cache && chmod 777 /tmp/mgnifams_cache

EXPOSE 8000
ENV DJANGO_SETTINGS_MODULE=mgnifams_site.settings
ENV PYTHONUNBUFFERED=0

RUN python manage.py collectstatic --noinput
RUN python manage.py migrate --fake
CMD gunicorn mgnifams_site.wsgi:application --bind 0.0.0.0:8000 --workers 3
