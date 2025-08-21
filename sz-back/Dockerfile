# Dockerfile (racine du repo)

FROM python:3.13-alpine

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apk add --no-cache \
    gcc g++ postgresql-dev python3-dev musl-dev libffi-dev make swig \
    jpeg-dev zlib-dev tzdata libxml2-dev libxslt-dev poppler-utils bash

COPY requirements.txt .
RUN pip install --upgrade pip setuptools \
 && pip install -r requirements.txt

COPY . .

EXPOSE 8000

# Run migrations, collectstatic puis Gunicorn
CMD ["sh", "-c", "\
    python manage.py migrate && \
    python manage.py collectstatic --noinput && \
    gunicorn salariz.wsgi:application --bind 0.0.0.0:8000 \
"]

# CMD ["sh", "-c", "\