# --- Etapa 1: Build (Construcción) ---
FROM python:3.12-slim AS builder

# Instalamos uv desde la imagen oficial
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Instalamos dependencias del sistema necesarias para compilar (gcc, libpq para postgres)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiamos el archivo de configuración y el readme (con asterisco por si no existe)
COPY pyproject.toml README.m* ./

# Truco: Creamos un README vacío si el COPY no encontró ninguno 
# Esto evita que el build de 'hatchling' falle
RUN touch README.md

# Creamos el entorno virtual en una ruta fija fuera de /app
# Instalamos las dependencias usando el pyproject.toml directamente
RUN uv venv /opt/venv && \
    uv pip install --no-cache --python /opt/venv/bin/python .

# --- Etapa 2: Runtime (Ejecución) ---
FROM python:3.12-slim

WORKDIR /app

# Configuramos las rutas para que Python y el Sistema encuentren el venv y tu código
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONPATH="/app" \
    PYTHONUNBUFFERED=1

# Instalamos solo las librerías de ejecución (libpq5 para que funcione la DB)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiamos el entorno virtual ya preparado desde la etapa anterior
COPY --from=builder /opt/venv /opt/venv

# Copiamos todo tu código fuente al contenedor
COPY . .

# Seguridad: Creamos un usuario que no sea root para correr la app
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

# El comando de arranque:
# 'app.main:app' asume que tienes una carpeta 'app' y dentro 'main.py'
# Si tu archivo main.py está en la raíz, cámbialo a "main:app"
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]