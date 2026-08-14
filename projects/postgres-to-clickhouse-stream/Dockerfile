FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY stream ./stream
COPY scripts ./scripts
COPY sql ./sql

CMD ["python", "-m", "stream.worker"]
