FROM python:3.13.7-alpine3.22

WORKDIR /app

# Instala dependencias
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

# Copia los archivos del projecto
COPY . .

CMD ["python", "app.py"]
