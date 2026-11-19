# TODO: Adapt `bonus1_license_service_oidc` After the pAIguard Refactoring

## Why this project is currently broken

`projects/proj1_pyguard` was renamed to `projects/proj1_paiguard` and turned
into **pAIguard**, an image content moderation library. The request-security
code this service uses was removed from the package:

- `PyGuard`, `PyGuard.Request`, `RequestBlocked`
- `pyguard.rules.PathTraversal` and `pyguard.rules.BruteForce`

Nothing in this project was changed. Until the tasks below are done:

- `uv sync` fails in `backend/`, because the path source `../proj1_pyguard`
  no longer exists.
- `docker compose build backend` fails, because the build context
  `pyguard: ../proj1_pyguard` no longer exists.
- `backend/license_service/middleware.py` cannot be imported.

The last version of the removed code is in the Git history:

```bash
git log --oneline -- projects/proj1_pyguard/src/pyguard
git show <commit>:projects/proj1_pyguard/src/pyguard/rules.py
git show <commit>:projects/proj1_pyguard/src/pyguard/engine.py
git show <commit>:projects/proj1_pyguard/src/pyguard/models.py
git show <commit>:projects/proj1_pyguard/tests/test_engine.py
```

## Decision to take first

pAIguard no longer provides request security, and this service does not
handle image uploads, so pAIguard is not a replacement. Choose one option:

- [ ] **Option A (recommended): move the rules into the service.** Copy
      `SecurityRule`, `PathTraversal`, `BruteForce`, the engine (`scan`,
      `check`, `RequestBlocked`), and the `Request` model from the Git history
      into a local module such as `backend/license_service/guard.py`. The
      rate limiting, the HTTP `429` responses, the Grafana alert, and the load
      test keep working as they are.
- [ ] **Option B: replace the rules with another solution**, for example a
      rate-limiting library or the reverse proxy. The HTTP `429` behavior, the
      Grafana alert, the load test, and Chapter 04 must then be adapted to the
      new solution.

The tasks below assume Option A. For Option B, the same files are affected.

## Required tasks

### Dependencies

- [ ] `backend/pyproject.toml`: remove `"pyguard==0.1.0"` from `dependencies`
      (line 10) and the `[tool.uv.sources]` entry
      `pyguard = { path = "../proj1_pyguard", editable = true }` (line 28).
- [ ] `backend/pyproject.toml`: add `pydantic` as a direct dependency if the
      copied `Request` and `ScanResult` models keep using it.
- [ ] `backend/uv.lock`: regenerate with `uv lock`. It still contains the
      editable source `../proj1_pyguard`.

### Docker and Compose

- [ ] `docker-compose.yml`: remove the additional build context
      `pyguard: ../proj1_pyguard` (line 26).
- [ ] `backend/Dockerfile`: remove `COPY --from=pyguard . /../proj1_pyguard`
      and its two comment lines (lines 13-15).
- [ ] Run `docker compose build backend` and `docker compose up` and check
      that the backend starts.

### Code

- [ ] Create the local module with the copied rules and engine.
- [ ] `backend/license_service/middleware.py`: replace
      `from pyguard import PyGuard, RequestBlocked` and
      `from pyguard.rules import PathTraversal, BruteForce` (lines 12-13)
      with imports from the local module.
- [ ] `backend/license_service/middleware.py`: adapt the uses of `PyGuard(...)`
      (line 63) and `PyGuard.Request(...)` (line 93) to the names chosen in the
      local module, and update the comments on lines 11, 62, and 84.

### Tests

- [ ] `backend/test/conftest.py`: the fixture `reset_pyguard` imports
      `PyGuardMiddleware` and calls `PyGuardMiddleware(protected_paths=...)`.
      That class did not exist in PyGuard any more even before this
      refactoring. Rewrite the fixture so that it resets the guard that
      `configure_middleware` stores in `app.state.guard`.
- [ ] Copy the 14 tests from `proj1_pyguard/tests/test_engine.py` and its
      `conftest.py` (Git history) into `backend/test/` and adapt the imports.
- [ ] Run the backend tests with `uv run pytest`.
- [ ] `backend/test/e2e/test_bruteforce.py`: update the three printed
      messages that mention PyGuard (lines 10, 36, 43) and run the script
      against the running stack.
- [ ] Run the load test described in `tests/README.md` and confirm that HTTP
      `429` is still returned.

### Documentation

- [ ] `backend/README.md`: update the PyGuard link to `proj1_pyguard/README.md`
      (line 7, now a dead link), the description on line 15, the Mermaid node
      `GUARD["PyGuard<br/>rate limiting"]` (line 22), line 76, and the table
      row on line 160.
- [ ] `tests/README.md`: update lines 98 and 112.
- [ ] `backend/plan.md`: update line 160.
- [ ] `grafana/README.md`: update the PyGuard mentions (lines 145-256).
- [ ] `docs/chapter-04/section-01.md`: update the PyGuard bullet with the dead
      link (line 10) and the embedded Compose file (line 55,
      `pyguard: ../proj1_pyguard`).
- [ ] `docs/chapter-04/section-03.md`: update the PyGuard mention on line 243.

## Optional improvements

- [ ] Rename `grafana/pyguard-http-429.alerting.yaml` and the names inside it
      (`PyGuard Stakeholders`, folder `PyGuard`, `PyGuard HTTP 429 Alert`,
      `pyguard_429_blocks`). If renamed, also update the volume mount shown in
      `grafana/README.md` (line 256) and the provisioning instructions there.
- [ ] Address the known limits of the brute-force rule that the old PyGuard
      README listed: it counts all requests to protected paths, not only
      failed authentication attempts, and it keeps its state in the memory of
      one worker process.
