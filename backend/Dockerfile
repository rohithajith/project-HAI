FROM python:3.9-slim

WORKDIR /app

# Copy requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend code
COPY . .

# Expose port for FastAPI
EXPOSE 8000

# Command to run the FastAPI server
CMD ["uvicorn", "fastapi_server:app", "--host", "0.0.0.0", "--port", "8000"]