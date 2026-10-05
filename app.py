from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime
import logging

app = Flask(__name__)

DB = "logs.db"

VALID_SERVICES = {
    "auth",
    "orders",
    "payments",
    "search",
    "notifications"
}

VALID_LEVELS = {
    "INFO",
    "WARN",
    "ERROR"
}


def init_db():
    conn = sqlite3.connect(DB)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            level TEXT NOT NULL,
            service TEXT NOT NULL,
            message TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


def validate(payload):
    errors = []

    # Validate log level
    if payload.get("level") not in VALID_LEVELS:
        errors.append("invalid level")

    # Validate service
    if payload.get("service") not in VALID_SERVICES:
        errors.append("invalid service")

    # Validate message
    if not payload.get("message"):
        errors.append("empty message")

    # Validate timestamp
    try:
        datetime.fromisoformat(payload.get("timestamp", ""))
    except (ValueError, TypeError):
        errors.append("invalid timestamp")

    return errors


@app.route("/ingest", methods=["POST"])
def ingest():

    payload = request.get_json(silent=True)

    # Validate JSON body
    if not payload:
        return jsonify({
            "error": "invalid JSON"
        }), 400

    # Validate log data
    errors = validate(payload)

    if errors:
        logging.warning(
            f"Rejected: {errors} | {payload}"
        )

        return jsonify({
            "error": "validation failed",
            "details": errors
        }), 400

    # Insert valid log into SQLite
    conn = sqlite3.connect(DB)

    conn.execute(
        """
        INSERT INTO logs
        (timestamp, level, service, message)
        VALUES (?, ?, ?, ?)
        """,
        (
            payload["timestamp"],
            payload["level"],
            payload["service"],
            payload["message"]
        )
    )

    conn.commit()
    conn.close()

    return jsonify({
        "status": "ok"
    }), 201


@app.route("/metrics/errors-by-service", methods=["GET"])
def errors_by_service():

    conn = sqlite3.connect(DB)

    rows = conn.execute("""
        SELECT
            service,
            COUNT(*) AS error_count
        FROM logs
        WHERE level = 'ERROR'
        GROUP BY service
        ORDER BY error_count DESC
    """).fetchall()

    conn.close()

    return jsonify([
        {
            "service": row[0],
            "errors": row[1]
        }
        for row in rows
    ])


@app.route("/metrics/hourly-volume", methods=["GET"])
def hourly_volume():

    conn = sqlite3.connect(DB)

    rows = conn.execute("""
        SELECT
            substr(timestamp, 1, 13) AS hour,
            COUNT(*) AS count
        FROM logs
        GROUP BY hour
        ORDER BY hour
    """).fetchall()

    conn.close()

    return jsonify([
        {
            "hour": row[0],
            "count": row[1]
        }
        for row in rows
    ])


@app.route("/health", methods=["GET"])
def health():

    return jsonify({
        "status": "healthy"
    }), 200


if __name__ == "__main__":

    init_db()

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False,
        use_reloader=False
    )