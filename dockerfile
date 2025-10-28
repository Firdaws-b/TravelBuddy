# Use a lightweight Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy dependency list and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files
COPY . .

# Expose FastAPI's default port
EXPOSE 8000

# Run your app
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
