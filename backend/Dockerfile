FROM python:3.9-slim

WORKDIR /app

RUN mkdir -p /app/logs && chmod 777 /app/logs

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY ./app /app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]