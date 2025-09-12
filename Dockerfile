# Etapa de build: instala dependencias en un venv aislado
FROM python:3.13.7-alpine3.22 AS builder

WORKDIR /app

COPY requirements.txt ./
# Crear entorno virtual y instalar dependencias
RUN python -m venv /opt/venv \
    && . /opt/venv/bin/activate \
    && pip install --no-cache-dir -r requirements.txt

############################################################
# Etapa de producción: imagen limpia con solo artefactos necesarios
FROM python:3.13.7-alpine3.22 AS production

ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Copia únicamente las dependencias ya instaladas desde el builder
COPY --from=builder /opt/venv /opt/venv

# Copia solo los archivos necesarios de la aplicación
COPY app.py ./
COPY flask_backend.py ./

EXPOSE 5000

CMD ["python", "app.py"]
