#!/bin/bash

# Start Nginx
service nginx start

# Start Gunicorn
gunicorn --workers=3 --bind unix:/app/app.sock TasteTailor.wsgi:application
