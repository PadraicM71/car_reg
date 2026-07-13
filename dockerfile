# Use a lightweight official Python image
FROM python:3.11-slim

# Create and switch to working directory
WORKDIR /app

# Install pip dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Expose default web port
EXPOSE 5000

# Start production server (Gunicorn) binding to dynamic port environment variable
CMD ["sh", "-c", "gunicorn --bind 0.0.0.0:${PORT:-5000} app:app"]
