FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY . .
ENV PYTHONPATH=/

CMD ["python", "-m", "app.main"]
