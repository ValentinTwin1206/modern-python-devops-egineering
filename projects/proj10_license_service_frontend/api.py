import os

import requests
import logging

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8080")
ADMIN_API_KEY = os.getenv("ADMIN_API_KEY", "dev-secret")


def create_license(user: str) -> dict:
    response = requests.post(
        f"{BACKEND_URL}/licenses",
        params={"user": user},
        headers={
            "X-API-Key": ADMIN_API_KEY,
        },
        timeout=10,
    )

    response.raise_for_status()

    return response.json()


def check_license(license_key: str) -> dict:
    response = requests.get(
        f"{BACKEND_URL}/licenses/{license_key}",
        timeout=10,
    )

    response.raise_for_status()

    return response.json()