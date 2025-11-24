# Use official Python base image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy only required files
COPY requirements.txt .
COPY README.md .
COPY Dockerfile .
COPY config ./config
COPY src ./src
COPY tests ./tests

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 8000

# Run the FastAPI app
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
