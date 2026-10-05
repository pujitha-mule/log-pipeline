# Log Ingestion & Query Pipeline

A small Flask service that ingests application logs via HTTP POST,
validates them, and stores them in SQLite. Provides SQL-based metrics endpoints.

## Stack
Python, Flask, SQL, SQLite, Docker

## Endpoints
- `POST /ingest` — receive a log (timestamp, level, service, message)
- `GET /metrics/errors-by-service` — error count per service
- `GET /metrics/hourly-volume` — log volume per hour
- `GET /health` — health check

## Validation Rules
1. Valid log level (INFO, WARN, ERROR)
2. Valid timestamp (ISO format)
3. Non-empty message
4. Service in whitelist
5. Valid JSON body
6. Required fields present

## Run
```bash
pip install -r requirements.txt
python app.py
```

In another terminal:
```bash
python generate_logs.py
```

## Test
```bash
curl -X POST http://localhost:5000/ingest \
  -H "Content-Type: application/json" \
  -d '{"timestamp":"2026-01-15T10:00:00","level":"ERROR","service":"auth","message":"test error"}'

curl http://localhost:5000/metrics/errors-by-service
curl http://localhost:5000/metrics/hourly-volume
```

## Docker
```bash
docker build -t log-pipeline .
docker run -p 5000:5000 log-pipeline
```