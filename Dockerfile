# --- Etapa 1: Constructor (Build) ---
FROM python:3.12-slim AS builder

# Instalar uv directamente desde el binario oficial
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Instalar dependencias necesarias para compilar librerías de C (como psycopg2)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Optimizamos caché: copiar archivos de dependencias primero
COPY pyproject.toml uv.lock ./

# Sincronizamos dependencias (crea .venv)
# --no-dev para no incluir librerías de testing en la imagen final
RUN uv sync --frozen --no-install-project --no-dev


# --- Etapa 2: Ejecución (Runtime) ---
FROM python:3.12-slim

# Variables de entorno
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

# Instalamos solo las librerías de sistema mínimas para ejecución
# libpq5 es necesaria para que el driver de Postgres funcione
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

# Copiar el entorno virtual desde el builder
COPY --from=builder /app/.venv /app/.venv

# Copiar el código del proyecto
# Importante: Esto copia la carpeta app/ y el archivo main.py
COPY . .

# Seguridad: Usuario no-root
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app
USER appuser

# Exponer el puerto de FastAPI
EXPOSE 8000

# Healthcheck (Ajustado a la ruta que definimos en main.py)
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Comando de ejecución
# Comando por defecto (será sobrescrito por docker-compose para incluir el sync)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]