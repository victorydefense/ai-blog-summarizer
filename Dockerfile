# Use an official Python runtime as a parent image
FROM python:3.11-slim-bullseye

# Set the working directory in the container
WORKDIR /app

# Copy requirements.txt and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose the port Render will use
EXPOSE 80

# Use the PORT environment variable provided by Render
CMD sh -c "uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-80}"