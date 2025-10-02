# ------------------
# 1. Base Image
# ------------------
# Use an official Python runtime as a parent image.
# 'slim-buster' is a smaller image, good for production.
FROM python:3.11-slim-buster

# ------------------
# 2. Environment Variables
# ------------------
# Set environment variables to prevent Python from writing .pyc files
# and to ensure print statements are sent straight to the logs.
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# ------------------
# 3. Install System Dependencies
# ------------------
# QUICK FIX for EOL Debian "Buster": Point to the archive repositories.
RUN echo "deb http://archive.debian.org/debian/ buster main" > /etc/apt/sources.list && \
    echo "deb http://archive.debian.org/debian-security buster/updates main" >> /etc/apt/sources.list

# Install dependencies needed for psycopg2 (PostgreSQL driver) and other potential libraries.
RUN apt-get update \
  && apt-get install -y --no-install-recommends gcc libpq-dev \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

# ------------------
# 4. Set Working Directory
# ------------------
# Set the working directory in the container.
WORKDIR /app

# ------------------
# 5. Install Python Dependencies
# ------------------
# Copy the requirements file first to leverage Docker layer caching.
# This way, dependencies are only re-installed if requirements.txt changes.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ------------------
# 6. Copy Application Code
# ------------------
# Copy the rest of the application's code into the container.
COPY TasteTailor .
COPY . .

# ------------------
# 7. Expose Port
# ------------------
# The port the container will listen on. Gunicorn will run on port 8000.
EXPOSE 8000

# ------------------
# 8. Run Application
# ------------------
# Run Gunicorn. 'TasteTailor.wsgi:application' should match your project's wsgi file path.
# Use the exec form to ensure signals are passed correctly.
CMD ["sh", "-c", "ls -la"]

