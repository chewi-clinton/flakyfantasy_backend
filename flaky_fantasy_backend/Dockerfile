# Use an official Python runtime as a parent image
FROM python:3.11.5-slim-bullseye

# Set environment variables
ENV PIP_DISABLE_PIP_VERSION_CHECK=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DJANGO_SETTINGS_MODULE=flaky_fantasy_backend.settings

# Install curl for healthcheck (cleaned up apt cache)
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Set the working directory in the container
WORKDIR /code

# Install system dependencies required for psycopg2
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

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose the port the app runs on
EXPOSE 8000

# Healthcheck - increased timeout and start-period for NeonDB cold starts
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=5 \
    CMD curl -f http://localhost:8000/api/health/ || exit 1

# Run migrations and start Gunicorn
CMD ["sh", "-c", "python manage.py migrate && gunicorn --bind 0.0.0.0:8000 --worker-tmp-dir /dev/shm flaky_fantasy_backend.wsgi:application --workers 1 --timeout 120 --max-requests 1000"]
