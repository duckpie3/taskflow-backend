FROM python:3.13.7-alpine3.22
WORKDIR /app

# Copy requirements.txt into the image
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

# Copy the rest of your project files
COPY . .

# Command to run your app
CMD ["python", "app.py"]
