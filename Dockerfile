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
# Add the project directory to the Python path to resolve module import errors.
ENV PYTHONPATH /app

# ------------------
# 3. Install System Dependencies
# ------------------
# QUICK FIX for EOL Debian "Buster": Point to the archive repositories.
RUN echo "deb http://archive.debian.org/debian/ buster main" > /etc/apt/sources.list && \
    echo "deb http://archive.debian.org/debian-security buster/updates main" >> /etc/apt/sources.list

# Install dependencies needed for psycopg2 (PostgreSQL driver), git, and other potential libraries.
RUN apt-get update \
  && apt-get install -y --no-install-recommends gcc libpq-dev git \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

# ------------------
# 4. Set Working Directory
# ------------------
# Set the working directory in the container.
WORKDIR /app

# ------------------
# 5. Copy Application Code
# ------------------
# Clone the repository's content directly into the current working directory (/app).
# The '.' at the end of the command is crucial.
RUN git clone https://github.com/NikhilSinghal1704/TasteTailor.git .

# ------------------
# 6. Install Python Dependencies
# ------------------
# Install dependencies from the cloned repository's requirements file.
RUN pip install --no-cache-dir -r requirements.txt

# ------------------
# 7. Django Static Files
# ------------------
# Collect static files for production.
RUN python manage.py collectstatic --noinput

# ------------------
# 8. Verify/Install Gunicorn
# ------------------
# Check if gunicorn is installed, and install it if it's not found.
# This provides a fallback if gunicorn is missing from requirements.txt.
RUN which gunicorn || pip install --no-cache-dir gunicorn

# ------------------
# 9. Expose Port
# ------------------
# The port the container will listen on. Gunicorn will run on port 8000.
EXPOSE 8000

# ------------------
# 10. Run Application
# ------------------
# Run Gunicorn to serve the Django application.
CMD ["sh", "-c", "ls -la && gunicorn TasteTailor.wsgi:application --bind 0.0.0.0:8000"]