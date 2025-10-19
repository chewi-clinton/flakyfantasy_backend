# Use an official Python runtime as a parent image
FROM python:3.11.5-slim-bullseye

# Set environment variables
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=pharmacy_backend.settings

# Set the working directory in the container
WORKDIR /code

# Install system dependencies required for psycopg2 and other packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY ./requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install gunicorn==22.0.0

# Copy the application code
COPY . .

# Create a non-root user and set permissions
RUN useradd -m appuser && chown -R appuser /code
USER appuser

# Collect static files (assumes STATIC_ROOT is configured in settings.py)
RUN python manage.py collectstatic --noinput

# Expose the port the app runs on
EXPOSE 8000

# Healthcheck to ensure the application is running
HEALTHCHECK --interval=30s --timeout=3s \
    CMD curl -f http://localhost:8000/health/ || exit 1

# Run migrations and start Gunicorn
CMD ["sh", "-c", "python manage.py migrate && gunicorn --bind 0.0.0.0:8000 --worker-tmp-dir /dev/shm pharmacy_backend.wsgi:application --workers 1 --timeout 120 --max-requests 1000"]