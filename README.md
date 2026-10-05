# Log Ingestion & Query Pipeline

A lightweight backend service for ingesting, validating, storing, and querying application logs.

The project provides a Flask REST API that accepts structured log events through HTTP POST requests, validates incoming data, stores valid records in SQLite, and exposes SQL-based endpoints for basic operational monitoring.

## Features

- REST API for application log ingestion
- JSON request validation
- Log-level validation
- Service whitelist validation
- ISO-format timestamp validation
- SQLite-based log storage
- SQL aggregation for operational metrics
- Error counts by service
- Hourly log-volume analysis
- Health-check endpoint
- Automated generation of 300 sample log events
- Docker support

## Tech Stack

| Technology | Purpose |
|---|---|
| Python | Application and log generation |
| Flask | REST API |
| SQLite | Log persistence |
| SQL | Data querying and aggregation |
| Requests | HTTP requests from the log generator |
| Docker | Containerization |

## Architecture

```text
                  +---------------------+
                  |    Log Generator    |
                  |  generate_logs.py   |
                  +----------+----------+
                             |
                             | HTTP POST
                             v
                  +---------------------+
                  |      Flask API      |
                  |       app.py        |
                  +----------+----------+
                             |
                             | Validation
                             v
                  +---------------------+
                  |   SQLite Database   |
                  |       logs.db       |
                  +----------+----------+
                             |
                             | SQL Queries
                             v
              +------------------------------+
              |      Metrics Endpoints       |
              |                              |
              |  Errors by Service           |
              |  Hourly Log Volume           |
              +------------------------------+
```

## Project Structure

```text
log-pipeline/
│
├── app.py                  # Flask API and database logic
├── generate_logs.py        # Generates sample log events
├── requirements.txt        # Python dependencies
├── Dockerfile              # Docker configuration
├── README.md               # Project documentation
├── .gitignore              # Git exclusions
│
├── logs.db                 # Generated SQLite database
└── app.log                 # Generated application log
```

`venv/`, `logs.db`, and `app.log` are local/generated files and should not be committed to GitHub.

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/ingest` | Receives and validates a log event |
| `GET` | `/metrics/errors-by-service` | Returns error counts grouped by service |
| `GET` | `/metrics/hourly-volume` | Returns log volume grouped by hour |
| `GET` | `/health` | Returns API health status |

## Log Ingestion

The `/ingest` endpoint accepts a JSON log event.

### Example Request

```json
{
  "timestamp": "2026-01-15T10:00:00",
  "level": "ERROR",
  "service": "auth",
  "message": "Authentication failed"
}
```

### Example Response

```json
{
  "status": "ok"
}
```

Valid records are stored in the SQLite database.

## Data Validation

Incoming log events are validated before insertion.

The API checks:

1. Log level
   - Allowed values: `INFO`, `WARN`, `ERROR`

2. Timestamp
   - Must use a valid ISO-format timestamp

3. Message
   - Must not be empty

4. Service
   - Must belong to the configured service whitelist

5. JSON body
   - Request must contain valid JSON

6. Required log information
   - Required fields must contain valid values

Invalid requests receive a `400 Bad Request` response with validation details.

### Example Invalid Response

```json
{
  "error": "validation failed",
  "details": [
    "invalid level",
    "invalid service",
    "empty message",
    "invalid timestamp"
  ]
}
```

## SQL Metrics

### Errors by Service

Endpoint:

```text
GET /metrics/errors-by-service
```

The API uses SQL aggregation with `GROUP BY` to count error-level logs for each service.

Example:

```json
[
  {
    "service": "payments",
    "errors": 67
  },
  {
    "service": "orders",
    "errors": 60
  }
]
```

### Hourly Log Volume

Endpoint:

```text
GET /metrics/hourly-volume
```

The API groups log records by hour and returns the number of events recorded during each hour.

Example:

```json
[
  {
    "hour": "2026-10-05T20",
    "count": 48
  },
  {
    "hour": "2026-10-05T21",
    "count": 52
  }
]
```

## Health Check

Endpoint:

```text
GET /health
```

Example:

```json
{
  "status": "healthy"
}
```

This endpoint can be used to verify that the API is running.

## Setup

### 1. Clone the Repository

```bash
git clone https://github.com/pujitha-mule/log-pipeline.git
cd log-pipeline
```

### 2. Create a Virtual Environment

Windows PowerShell:

```powershell
python -m venv venv
```

Activate it:

```powershell
.\venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Start the API

```bash
python app.py
```

The API will run on:

```text
http://127.0.0.1:5000
```

## Generate Sample Logs

Open another terminal and activate the virtual environment:

```powershell
.\venv\Scripts\Activate.ps1
```

Run:

```powershell
python generate_logs.py
```

The generator creates and sends 300 sample log events to the Flask `/ingest` endpoint.

Example verification:

```text
Generation complete.
Successful: 300
Failed: 0
```

## Testing

### Health Check

```powershell
curl.exe http://127.0.0.1:5000/health
```

Expected:

```json
{
  "status": "healthy"
}
```

### Check Errors by Service

```powershell
curl.exe http://127.0.0.1:5000/metrics/errors-by-service
```

### Check Hourly Volume

```powershell
curl.exe http://127.0.0.1:5000/metrics/hourly-volume
```

### Test Log Ingestion

For Windows PowerShell:

```powershell
$body = @{
    timestamp = "2026-01-15T10:00:00"
    level     = "ERROR"
    service   = "auth"
    message   = "Test error"
} | ConvertTo-Json

Invoke-RestMethod `
    -Uri "http://127.0.0.1:5000/ingest" `
    -Method POST `
    -ContentType "application/json" `
    -Body $body
```

Expected:

```text
status
------
ok
```

## Docker

### Build the Image

```bash
docker build -t log-pipeline .
```

### Run the Container

```bash
docker run -p 5000:5000 log-pipeline
```

The API will be available at:

```text
http://localhost:5000
```

Test it with:

```bash
curl http://localhost:5000/health
```

## Project Workflow

```text
Generate Logs
     |
     v
HTTP POST /ingest
     |
     v
Validate Request
     |
     v
Store Valid Log
     |
     v
SQLite Database
     |
     v
SQL Aggregation
     |
     v
Operational Metrics
```

## What This Project Demonstrates

- Python backend development
- REST API development
- HTTP-based data ingestion
- Data validation
- SQLite database operations
- SQL aggregation and `GROUP BY`
- Basic data pipeline concepts
- API testing
- Docker containerization

## Verification

The log generator was tested with:

```text
300 log events
300 successful requests
0 failed requests
```

This verifies the end-to-end flow from log generation to API ingestion and database storage.

## Author

**Pujitha Mule**

B.Tech Computer Science & Engineering — 2026

GitHub:  
https://github.com/pujitha-mule

## License

This project is intended for learning, portfolio, and demonstration purposes.