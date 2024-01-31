FROM python:3.11

# Set the working directory in the container
WORKDIR /usr/src/app

# Copy the requirements file into the container at /usr/src/app
COPY requirements.txt ./

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /usr/src/app
COPY . .

# Set environment variables
ENV EMAIL_HOST_USER=no-reply@mikostop.com \
    EMAIL_HOST_PASSWORD=Mikostop123@ \
    SECRET_KEY=django-insecure-px%_nj38apl*^-ai215*n&s3k$+k#^tiuawp1%0y)gekn1j=5q \
    DEBUG=True \
    DB_PASSWORD=ZO4BvuhnJOmCOV4z \
    DB_USER=postgres.tpsaiyfafetdruhimdlj \
    DB_HOST=aws-0-ap-southeast-2.pooler.supabase.com \
    DB_PORT=6543 \
    DB_NAME=postgres

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Define environment variable
ENV NAME World

# Run the web service on container startup. Here we use the gunicorn
# webserver, with one worker process and 8 threads.
# For environments with multiple CPU cores, increase the number of workers
# to be equal to the cores available.
# Timeout is set to 0 to disable the timeouts of the workers to allow Cloud Run to handle instance scaling.
CMD exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 8 --timeout 0 diagnosa_backend.wsgi:application
