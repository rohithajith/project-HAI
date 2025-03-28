FROM python:3.9-slim

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir flask flask-cors requests

# Copy app code
COPY . .

# Expose port
EXPOSE 5003

# Environment variables
ENV FLASK_APP=app.py
ENV PORT=5003
ENV BACKEND_URL=http://backend:8000

# Command to run the Flask server
CMD ["flask", "run", "--host=0.0.0.0", "--port=5003"]