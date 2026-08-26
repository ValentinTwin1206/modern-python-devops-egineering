#!/usr/bin/env python3

import time
import requests

URL = "http://127.0.0.1:8800/licenses"
INVALID_KEY = "definitely-wrong-key"
ATTEMPTS = 7

print("Testing PyGuard brute-force protection...")
print(f"Target: {URL}")
print()

for i in range(1, ATTEMPTS + 1):
    try:
        response = requests.post(
            URL,
            headers={
                "X-API-Key": INVALID_KEY,
                "Content-Type": "application/json",
            },
            json={"user": "bruteforce-test"},
        )

        status_code = response.status_code

    except requests.RequestException as exc:
        print(f"Attempt {i}: request failed: {exc}")
        continue

    print(f"Attempt {i}: HTTP {status_code}")

    if status_code == 429:
        print()
        print(
            f"SUCCESS: PyGuard blocked the source after {i - 1} failed attempts."
        )
        raise SystemExit(0)

    time.sleep(0.2)

print()
print("FAILURE: PyGuard did not return HTTP 429.")
raise SystemExit(1)