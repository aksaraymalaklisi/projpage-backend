# I have specified the path to /usr/src/app.? Why? It was working fine before. Except for the entrypoint script.
# Probably because some tyrannical entity with no respect for human life was responsible for whatever makes ENTRYPOINT work like this.
# As a note: I, for some reason, decided to try and move entrypoint.sh to the Django project folder (/usr/src/app/trackproj/). 
# It started failing again.

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
WORKDIR /usr/src/app

# Install dependencies
COPY trackproj/requirements.txt /usr/src/app/requirements.txt
RUN pip install --upgrade pip \ 
    && pip install -r requirements.txt

# Copy project files
COPY . /usr/src/app/

# Set entrypoint script permissions
RUN chmod +x /usr/src/app/entrypoint.sh

# Set new work directory to run Django (oops)
WORKDIR /usr/src/app/trackproj

# Set entrypoint
ENTRYPOINT ["/usr/src/app/entrypoint.sh"]

# Expose port
EXPOSE 8000