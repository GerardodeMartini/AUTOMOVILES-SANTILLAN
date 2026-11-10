# ==========================================
# DOCKERFILE - AUTOMÓVILES SANTILLÁN
# Optimizado para despliegues en Coolify
# ==========================================
FROM python:3.11-slim

# Variables de entorno para Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Instalar librerías de sistema necesarias para PostgreSQL y Pillow (soporte WebP/JPG)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    libjpeg-dev \
    zlib1g-dev \
    libwebp-dev \
    && rm -rf /var/lib/apt/lists/*

# Directorio principal de la aplicación
WORKDIR /app

# Copiar e instalar dependencias de Python
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el resto del código
COPY . /app/

# Crear carpetas necesarias para archivos estáticos y subidas
RUN mkdir -p /app/staticfiles /app/media

# Dar permisos de ejecución al script de arranque
RUN chmod +x /app/entrypoint.sh

# Puerto estándar expuesto
EXPOSE 8000

# Ejecutar punto de entrada
ENTRYPOINT ["/app/entrypoint.sh"]
