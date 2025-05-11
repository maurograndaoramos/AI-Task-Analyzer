# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container at /app
COPY ./backend/requirements.txt /app/requirements.txt

# Install uv and then use it to install packages from requirements.txt
# Using --no-cache-dir to reduce image size
RUN pip install --no-cache-dir uv && \
    uv pip install --no-cache-dir -r /app/requirements.txt --system

# Copy the rest of the application code into the container at /app
COPY ./backend/app /app/app
COPY ./.env.example /app/.env.example
# Note: .env file itself should not be copied into the image for security.
# It should be provided at runtime.

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Define environment variable for the application to run in production mode (optional)
# ENV APP_ENV production

# Command to run the application using Uvicorn
# The host 0.0.0.0 makes the application accessible from outside the container
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
