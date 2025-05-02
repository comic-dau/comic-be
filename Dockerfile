# syntax=docker/dockerfile:1

FROM python:3.10-slim

# Prevents Python from writing pyc files
ENV PYTHONDONTWRITEBYTECODE=1
# Keeps Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .
# Make sure the entrypoint script is executable
RUN chmod +x /app/docker-entrypoint.sh

# Expose the port the app runs on
EXPOSE 8000

# Run migrations and start the application
# Use --nothreading and --noreload to avoid SSL issues on Windows Docker
CMD ["bash", "-c", "sleep 10 && python manage.py migrate && python manage.py runserver 0.0.0.0:8000 --nothreading --noreload"]