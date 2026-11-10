#!/bin/sh
set -e

echo "==> [Coolify] Ejecutando migraciones de base de datos..."
python manage.py migrate --noinput

echo "==> [Coolify] Asegurando superusuario inicial..."
python manage.py crear_superusuario || true

echo "==> [Coolify] Recolectando archivos estáticos..."
python manage.py collectstatic --noinput

echo "==> [Coolify] Iniciando Gunicorn en puerto 8000..."
exec gunicorn concesionaria.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --threads 2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -

