FROM python:3.9-slim-buster

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY finetunedmodel-merged /app/finetunedmodel-merged
COPY backend/local_model_chatbot.py /app/local_model_chatbot.py
COPY backend/flask_app.py /app/flask_app.py

EXPOSE 8001
EXPOSE 5001

CMD ["python", "/app/flask_app.py"]