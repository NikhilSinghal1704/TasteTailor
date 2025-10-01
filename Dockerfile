# Use the official Python image for Django and Gunicorn
FROM python:3.10-slim

# Install required packages
RUN apt-get update && apt-get install -y \
    nginx \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Clone the Django application from GitHub
RUN git clone https://github.com/NikhilSinghal1704/Portfolio_Creator .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt


# Expose port 8000 for Nginx
EXPOSE 8000

# Nginx configuration
COPY ./nginx/nginx.conf /etc/nginx/nginx.conf
COPY ./nginx/app.conf /etc/nginx/conf.d/app.conf

# Copy the start script to the container
COPY ./start.sh /app/start.sh

# Make the start script executable
RUN chmod +x /app/start.sh

# Use the start.sh script to start Nginx and Gunicorn
CMD ["./start.sh"]
