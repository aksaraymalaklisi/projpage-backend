#!/bin/sh
set -e

# Wait for the database to be ready
until mysqladmin ping -h"$DJANGO_DB_HOST" -P"$DJANGO_DB_PORT" --silent; do
  echo "Waiting for database..."
  sleep 2
done

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Create superuser if it doesn't exist
if [ "$DJANGO_SUPERUSER_USERNAME" ] && [ "$DJANGO_SUPERUSER_EMAIL" ] && [ "$DJANGO_SUPERUSER_PASSWORD" ]; then
  python manage.py createsuperuser --noinput --username "$DJANGO_SUPERUSER_USERNAME" --email "$DJANGO_SUPERUSER_EMAIL" || true
fi

# Start Gunicorn
exec gunicorn trackproj.wsgi:application --bind 0.0.0.0:8000
