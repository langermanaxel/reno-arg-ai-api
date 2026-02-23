# --- Etapa 1: Constructor (Build) ---
FROM python:3.12-slim AS builder

# Instalar uv directamente desde el binario oficial
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Optimizamos caché: primero archivos de dependencias
COPY pyproject.toml uv.lock ./

# Sincronizamos dependencias (crea .venv con todas las librerías de la app)
RUN uv sync --frozen --no-install-project --no-dev


# --- Etapa 2: Ejecución (Runtime) ---
FROM python:3.12-slim

# Variables de entorno
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app \
    PATH="/app/.venv/bin:$PATH"

WORKDIR /app

# 1. Instalamos dependencias del sistema
# 2. Instalamos httpx globalmente para que sync_models.py siempre funcione
RUN apt-get update && apt-get install -y \
    curl \
    libpq-dev \
    && pip install --no-cache-dir httpx \
    && rm -rf /var/lib/apt/lists/*

# Copiar el entorno virtual desde la etapa de construcción
COPY --from=builder /app/.venv /app/.venv

# Copiar el resto del código del proyecto
COPY . .

# Seguridad: Usuario no-root para ejecución
RUN adduser --disabled-password --gecos '' appuser && \
    chown -R appuser:appuser /app
USER appuser

# Exponer el puerto de FastAPI
EXPOSE 8000

# Healthcheck apuntando a la ruta de salud de tu API
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health || exit 1

# Comando por defecto (será sobrescrito por docker-compose para incluir el sync)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]