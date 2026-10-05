import requests
import random
from datetime import datetime, timedelta

URL = "http://127.0.0.1:5000/ingest"

SERVICES = [
    "auth",
    "orders",
    "payments",
    "search",
    "notifications"
]

LEVELS = [
    "INFO",
    "WARN",
    "ERROR"
]


def generate(n=300):

    success = 0
    failed = 0

    for i in range(n):

        payload = {
            "timestamp": (
                datetime.now() -
                timedelta(minutes=random.randint(0, 300))
            ).isoformat(),

            "level": random.choice(LEVELS),

            "service": random.choice(SERVICES),

            "message": f"Sample log event {i + 1}"
        }

        try:

            response = requests.post(
                URL,
                json=payload,
                timeout=5
            )

            if response.status_code == 201:
                success += 1
            else:
                failed += 1
                print(
                    f"Request {i + 1} failed: "
                    f"{response.status_code} "
                    f"{response.text}"
                )

        except requests.exceptions.RequestException as e:

            failed += 1

            print(
                f"Request {i + 1} failed: {e}"
            )

        if (i + 1) % 10 == 0:
            print(
                f"Progress: {i + 1}/{n} | "
                f"Success: {success} | "
                f"Failed: {failed}"
            )

    print("\nGeneration complete.")
    print(f"Successful: {success}")
    print(f"Failed: {failed}")


if __name__ == "__main__":
    generate(300)