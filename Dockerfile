# Use an official Python runtime as a parent image
FROM python:3.9-slim-buster

# Set environment variables
ENV PYTHONUNBUFFERED 1

# Create and set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . /app/

ENV PATH="/usr/local/bin:$PATH"

# Run gunicorn
CMD ["gunicorn", "diagnosa_backend.wsgi:application", "--bind", "0.0.0.0:8000"]