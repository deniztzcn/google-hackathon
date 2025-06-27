# Use an official lightweight Python image.
# https://hub.docker.com/_/python
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the dependencies file and install them
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Command to run the application using Gunicorn
# Gunicorn is a production-ready WSGI server.
# It listens on 0.0.0.0 (all interfaces) and port 8080, which Cloud Run expects.
# "app:app" means "in the file app.py, run the variable named app".
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]