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

# Create superuser if it doesn't exist (real)
if [ "$DJANGO_SUPERUSER_USERNAME" ] && [ "$DJANGO_SUPERUSER_EMAIL" ] && [ "$DJANGO_SUPERUSER_PASSWORD" ]; then
    python manage.py shell -c "
import os
from django.contrib.auth import get_user_model

User = get_user_model()
username = os.environ['DJANGO_SUPERUSER_USERNAME']
email = os.environ['DJANGO_SUPERUSER_EMAIL']
password = os.environ['DJANGO_SUPERUSER_PASSWORD']

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    print(f'Superuser {username} created successfully.')
else:
    print(f'Superuser {username} already exists. Skipping creation.')
"
fi

# Start Daphne
exec daphne -b 0.0.0.0 -p 8000 trackproj.asgi:application