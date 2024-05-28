FROM python:3.11
LABEL authors="sandyr"

WORKDIR /app
ADD mgnifams_site .
ADD requirements.txt .

RUN pip install -r requirements.txt

EXPOSE 8000
ENV DJANGO_SETTINGS_MODULE=mgnifams_site.settings
ENV PYTHONUNBUFFERED=0

RUN python manage.py collectstatic --noinput
RUN python manage.py migrate --fake
CMD python manage.py runserver 0.0.0.0:8000
