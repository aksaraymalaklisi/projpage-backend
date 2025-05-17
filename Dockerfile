# Use official Python image (based on what was used during development)
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies (required for MySQL client)
# Had to redo this. I love MySQL client installation on Docker.
# MySQL client installation makes me rethink my life choices.
# Last line is used to clean up apt cache to reduce image size
RUN apt-get update \
    && apt-get install -y python3-dev default-mysql-client default-libmysqlclient-dev build-essential pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Install dependencies
COPY trackproj/requirements.txt /app/requirements.txt
RUN pip install --upgrade pip \ 
    && pip install -r requirements.txt

# Copy project files
COPY . /app/

# Set new work directory to run Django (oops)
WORKDIR /app/trackproj

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 8000