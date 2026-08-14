FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY scripts ./scripts
COPY sql ./sql
COPY postgres ./postgres
COPY checks ./checks
COPY sample_data ./sample_data
ENV PYTHONPATH=/app

CMD ["python", "scripts/stream_worker.py"]
