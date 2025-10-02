# ------------------
# 1. Base Image
# ------------------

FROM python:3.11-slim-buster

# ------------------
# 2. Environment Variables
# ------------------

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# ------------------
# 3. Install System Dependencies
# ------------------
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

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ------------------
# 6. Copy Application Code
# ------------------

COPY . .

# ------------------
# 7. Expose Port
# ------------------

EXPOSE 8000

# ------------------
# 8. Run Application
# ------------------

CMD ["gunicorn", "TasteTailor.wsgi:application", "--bind", "0.0.0.0:8000"]