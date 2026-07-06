#!/bin/sh
set -e

echo "Waiting for PostgreSQL..."

until python -c "
import psycopg
psycopg.connect(
    dbname='$DATABASE_NAME',
    user='$DATABASE_USER',
    password='$DATABASE_PASSWORD',
    host='$DATABASE_HOST',
    port='$DATABASE_PORT'
)
print('Database is ready')
" >/dev/null 2>&1
do
    echo "Database unavailable, waiting..."
    sleep 2
done

echo "Running migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Starting Gunicorn..."
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3