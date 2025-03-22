# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set the working directory in the container
WORKDIR /app

# Copy requirements.txt and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code
COPY . .

# Expose port 80 for the container
EXPOSE 80

# Run the FastAPI app with uvicorn
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "80"]