import os

import requests

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8080")


def get_license(access_token: str) -> dict:
    response = requests.get(
        f"{BACKEND_URL}/licenses",
        headers={
            "Authorization": f"Bearer {access_token}",
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