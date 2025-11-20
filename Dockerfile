# Etapa de build
FROM python:3.13.7-alpine3.22 AS builder

WORKDIR /app

COPY requirements.txt ./

# Instalar dependencias de compilación para Postgres ---
RUN apk add --no-cache postgresql-dev gcc python3-dev musl-dev

# Crear entorno virtual y instalar dependencias
RUN python -m venv /opt/venv \
    && . /opt/venv/bin/activate \
    && pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir gunicorn supervisor

############################################################
# Etapa de producción
FROM python:3.13.7-alpine3.22 AS production

ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Instalar librería cliente de Postgres para ejecución ---
RUN apk add --no-cache libpq

# Copia únicamente las dependencias ya instaladas desde el builder
COPY --from=builder /opt/venv /opt/venv

# Copia solo los archivos necesarios de la aplicación
COPY app.py ./
COPY flask_backend.py ./
COPY supervisord.conf /opt/supervisord.conf

EXPOSE 5000

RUN addgroup -g 1000 appuser && \
    adduser -u 1000 -G appuser -s /bin/sh -D appuser && \
    mkdir -p /app/instance /app/data && \
    chown -R appuser:appuser /app

USER appuser

CMD ["supervisord","-c","/opt/supervisord.conf"]
