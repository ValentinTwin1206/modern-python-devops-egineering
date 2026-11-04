# PyGuard

**PyGuard** is a lightweight, framework-independent Python security engine for inspecting incoming web requests before they reach application handlers.

It currently provides:

-   **Path traversal protection**
-   **Brute-force protection** for configured endpoints

PyGuard separates its security engine and rules from framework integration. This lets applications use the same security rules with their own middleware.

## Installation

### Requirements

-   Python 3.9+
-   `uv` or `pip`

### Installation

With `uv`, add PyGuard to your project dependencies:

```bash
uv add pyguard==0.1.0
```

Then install the dependencies:

``` bash
uv sync
```

## Usage

### Create a `PyGuard` instance

Create a `PyGuard` instance and pass the security rules you want to enable. `PyGuard` runs the configured rules when a request is checked:

``` python
from pyguard import PyGuard
from pyguard.rules import PathTraversal, BruteForce

guard = PyGuard(
    rules=[
        PathTraversal(),
        BruteForce(
            paths=["/login", "/auth"],
            max_attempts=5,
            window=60,
            block_duration=300,
        ),
    ]
)

# PyGuard provides a framework-independent request model through `PyGuard.Request`:
request = PyGuard.Request(
    method="GET",
    path="/download",
    query="file=../../etc/passwd",
    source="203.0.113.10",
    body=body.decode("utf-8", errors="replace"),
)

try:
    guard.check(request)
except RequestBlocked as exc:
    print(f"Request blocked: {exc}")
```

`guard.check(request)` returns the request when no rule blocks it. It raises `RequestBlocked` when a configured rule identifies the request as blocked.

### Brute-Force Protection

Configure the endpoints that should be monitored:

``` python
from pyguard import PyGuard
from pyguard.rules import BruteForce

guard = PyGuard(
    rules=[
        BruteForce(
            paths=["/login", "/auth"],
            max_attempts=5,
            window=60,
            block_duration=300,
        )
    ]
)
```

Parameters:

  Parameter          Description
  ------------------ --------------------------------------------------
  `paths`            Request paths monitored by the rule.
  `max_attempts`     Number of requests that trigger a block.
  `window`           Time window, in seconds, used to count requests.
  `block_duration`   How long a source remains blocked, in seconds.

> Note: The current implementation counts requests to configured paths. It does not yet distinguish successful requests from failed authentication attempts.

## Drawbacks

- **Brute-force detection:** PyGuard currently counts all requests to configured protected paths, regardless of whether authentication succeeds or fails. Successful authentication attempts do not reset the counter. This may lead to false positives.

- **Multi-worker support:** PyGuard currently stores brute-force tracking data in local memory. Consequently, request counters and temporary blocks are not shared between multiple worker processes or server instances. Support for a shared storage backend such as Redis may be considered in the future.