#!/bin/bash

# Script para ejecutar el servicio de favoritos localmente

# Activar entorno virtual si existe
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Configurar variables de entorno
export MONGODB_HOST=${MONGODB_HOST:-mongodb://localhost:27017/}
export AUTH_SERVICE_URL=${AUTH_SERVICE_URL:-http://localhost:3000}
export DJANGO_SETTINGS_MODULE=core.settings

# Ejecutar migraciones (opcional para MongoDB con djongo)
python manage.py makemigrations
python manage.py migrate

# Iniciar servidor
python manage.py runserver 0.0.0.0:3006


