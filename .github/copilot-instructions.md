# GitHub Copilot Instructions — Talent Acquisition Agent

> These instructions govern how Copilot (and all AI assistants) should reason about,
> generate, and review code in this repository. Follow them in every suggestion.

---

## 1. Project Identity

| Property | Value |
|---|---|
| **Name** | `talent-acquisition-agent` (Job Agent) |
| **Language** | Python 3.12+ |
| **Package Manager** | `uv` — always use `uv run`, `uv sync`, `uv add` |
| **Entry Points** | `src/main.py` (CLI), `src/server.py` (HTTP API) |
| **Config Pattern** | 12-Factor App — all config from environment variables via `pydantic-settings` |
| **Async Runtime** | `asyncio` — all I/O is async |
| **HTTP Framework** | FastAPI + Uvicorn |
| **Documentation** | Sphinx (`docs/source/`) — deployed to GitHub Pages |

---

## 2. Architecture Invariants

These rules reflect the 12-Factor methodology baked into this project. **Never violate them.**

### Factor III — Config
- All configuration lives in `src/settings.py` via `pydantic-settings` `BaseSettings`.
- **Never hardcode** API keys, hostnames, ports, or paths. Always add a new `Field(...)` in `Settings`.
- Secrets come from `.env` (local) or CI/CD environment variables (production). Never commit `.env`.

### Factor XI — Logs
- Always use the project logger: `from config import logger`
- **Never use `print()`** in production code paths — only in standalone `if __name__ == "__main__"` test blocks.
- Log format is JSON in production, human-readable in development (controlled by `ENV_MODE`).

### Factor VI — Processes
- All services must be stateless. Shared state goes into `data/applications.json` (tracker) or a configured `DATABASE_URL`.
- All I/O functions must be `async def`. Use `asyncio.gather()` for parallelism.

### Factor IV — Backing Services
- External services (Remote OK, Indeed, LinkedIn, Twilio, SMTP) are treated as attached resources — swappable via env vars.
- Network calls belong exclusively in `src/modules/`. Never make HTTP calls from `server.py` or `main.py` directly.

---

## 3. Code Style & Conventions

### Python Style
```python
# ✅ Correct: async functions for all I/O
async def search_jobs() -> list[Job]:
    async with aiohttp.ClientSession() as session:
        ...

# ❌ Wrong: sync I/O in an async service
def search_jobs():
    import requests
    return requests.get(url).json()
```

- Use **dataclasses** (`@dataclass`) for plain data containers (`Job`, `JobApplication`, `NotificationConfig`).
- Use **Pydantic `BaseModel`** only for FastAPI request/response schemas.
- Type-annotate every function signature — input args and return types.
- Keep modules focused: one class per file in `src/modules/`.
- Private helpers are prefixed with `_`: `_load_config()`, `_search_remote_ok()`.

### Naming
| Concept | Convention | Example |
|---|---|---|
| Classes | `PascalCase` | `JobSearcher`, `ApplicationTracker` |
| Functions / methods | `snake_case` | `search_all()`, `notify_new_jobs()` |
| Constants / env vars | `UPPER_SNAKE_CASE` | `MAX_JOBS_PER_SEARCH` |
| Private methods | `_snake_case` | `_load()`, `_save()` |
| Files | `snake_case.py` | `job_search.py` |

### Imports
Always import from the project's own modules using bare names (not relative), since `src/` is on `sys.path`:
```python
# ✅ Correct
from config import logger
from settings import get_settings
from modules.job_search import JobSearcher

# ❌ Wrong
from src.config import logger
from .settings import get_settings
```

---

## 4. Module Responsibilities (Don't Cross the Boundary)

```
src/
├── config.py       → Logging setup ONLY. No business logic.
├── settings.py     → Environment config ONLY. No I/O.
├── main.py         → Orchestration ONLY. Calls modules, no logic.
├── server.py       → HTTP API ONLY. Thin wrappers over modules.
└── modules/
    ├── job_search.py     → Fetch jobs from external boards.
    ├── notifications.py  → Send email / SMS alerts.
    └── tracker.py        → Read/write applications.json.
```

**Adding a new feature?**
- New external API → new file in `src/modules/`
- New HTTP endpoint → add route in `server.py`, delegate to module
- New config value → add `Field(...)` in `settings.py`
- New shared data model → add `@dataclass` in the owning module

---

## 5. Adding New Job Board Sources

When adding a new scraper (e.g., `_search_greenhouse()`):
1. Add a method `async def _search_<source>(self) -> list[Job]:` in `JobSearcher`.
2. Add a feature-flag field in `Settings`: `greenhouse_enabled: bool = Field(default=False, ...)`.
3. Guard the call in `search_all()`:
   ```python
   if settings.greenhouse_enabled:
       tasks.append(self._search_greenhouse())
   ```
4. Handle **all** exceptions inside the scraper — never let a failed board crash the whole pipeline.
5. Document the new source in `docs/source/configuration.rst`.

---

## 6. Error Handling

```python
# ✅ Correct: isolate failures per source, log with context
try:
    async with session.get(url, timeout=10) as resp:
        ...
except asyncio.TimeoutError:
    logger.warning("Remote OK timeout", extra={"url": url, "role": role})
except Exception as e:
    logger.error("Remote OK search failed", extra={"error": str(e), "role": role})

# ❌ Wrong: bare except with print
except:
    print("error")
```

- Use `asyncio.gather(*tasks, return_exceptions=True)` so one failing source doesn't kill others.
- Check `isinstance(result, Exception)` after `gather` — log and skip failed results.
- HTTP errors: raise `HTTPException` with appropriate status codes in FastAPI routes.

---

## 7. Testing Guidelines & Best Practices

- **Framework**: Use `pytest` for all tests.
- **Async Tests**: Use `pytest-asyncio`. Mark async tests with `@pytest.mark.asyncio`.
- **Coverage**: Aim for at least 80% code coverage. Run with `uv run pytest --cov=src`.
- **Mocks**:
    - Use `aioresponses` for mocking `aiohttp` requests.
    - Use `unittest.mock.patch` for mocking internal components or side effects (like sending emails/SMS).
- **Fixtures**: Use `pytest` fixtures for common setup (e.g., a pre-configured `JobSearcher` or a temporary `ApplicationTracker`).
- **Isolation**:
    - Tests must not rely on local environment variables or files.
    - Use temporary directories for tests that write to disk (`tmp_path` fixture).
    - Mock all external API calls.
- **Naming**: Test files must start with `test_` and be located in the `tests/` directory.
- Tests should be added for every new feature, bug fix, and edge case. No code is too small to test.

```python
# ✅ Correct: Async test with mocking
import pytest
from aioresponses import aioresponses
from modules.job_search import JobSearcher

@pytest.mark.asyncio
async def test_search_remote_ok(job_searcher):
    with aioresponses() as m:
        m.get("https://remoteok.com/api?tag=python", payload=[{}, {"company": "Test", "position": "Dev", "url": "..."}])
        jobs = await job_searcher._search_remote_ok()
        assert len(jobs) == 1
        assert jobs[0].company == "Test"
```

---

## 8. FastAPI / HTTP API Rules

- Every route must have a **docstring** (it becomes the OpenAPI description).
- Request/response models must be explicit `BaseModel` subclasses — no raw `dict` returns except for health checks.
- Use `HTTPException` with proper status codes (`404`, `409`, `422`).
- Application state (tracker, searcher) should be instantiated **per-request** (current pattern), not stored as global app state, to maintain statelessness.
- Lifespan events (`@asynccontextmanager async def lifespan`) handle startup/shutdown logging.

---

## 9. Documentation Standards

### Docstrings
Use Google-style docstrings on all public classes and methods:
```python
async def search_all(self) -> list[Job]:
    """Search all configured job board sources in parallel.

    Returns:
        list[Job]: Deduplicated list of job listings found across all sources.

    Raises:
        None: Exceptions are caught internally per source.
    """
```

### RST Pages
- All new modules must have a corresponding `.rst` file under `docs/source/api/`.
- Follow the existing pattern in `docs/source/api/main.rst`.
- Build docs locally before committing: `cd docs && uv run sphinx-build -b html source/ build/html/dev`
- Every new feature should contain documentation updates.

---

## 10. CI/CD & Git Workflow

### Branch Strategy
| Branch | Purpose |
|---|---|
| `main` | Production-ready. Triggers doc deploy (`0.1/` folder) |
| `doc_build` | Documentation changes |
| Feature branches | `feat/<name>`, e.g. `feat/linkedin-scraper` |
| Bug fixes | `fix/<name>`, e.g. `fix/tracker-duplicate` |

### Commit Messages (Conventional Commits)
```
feat(modules): add Greenhouse job board scraper
fix(tracker): deduplicate applications by URL
docs(api): add server.py RST page
chore(deps): update aiohttp to 3.9.x
refactor(settings): consolidate DB settings
```

### Docs Versioning
- Version in `pyproject.toml` drives the docs folder on GitHub Pages.
- `0.1.0` → `https://rakrsh.github.io/talent-acquisition-agent/0.1/`
- `0.1.dev0` → `.../dev/`
- Always bump `pyproject.toml` version before releasing a new doc version.

---

## 11. Security Rules

- **Never log** `sender_password`, `twilio_token`, or any secret field — not even partially.
- Validate all user-supplied strings before using in URL construction (job board scrapers).
- The `.env` file is in `.gitignore` — **never stage it**.
- Add new secrets to `.env.example` with placeholder values and a comment explaining the format.
- Prefer `aiohttp` over `requests` for all async HTTP — never import `requests` in async code paths.

---

## 12. Prompt Engineering for AI Assistants

When prompting Copilot or any LLM within this project context:

### Be Specific About the Layer
> ✅ "Add a `_search_greenhouse(self) -> list[Job]` async method to `JobSearcher` in `job_search.py`"
> ❌ "Add greenhouse job search"

### Reference the Settings Pattern
> ✅ "Add a `greenhouse_enabled` boolean Field to `Settings` with env alias `GREENHOUSE_ENABLED`, default `False`"

### Mention the Logger, Not Print
> ✅ "Log errors using `logger.error()` from `config import logger`"

### Specify Async Correctly
> ✅ "Write an async method that uses `aiohttp.ClientSession` with a 10s timeout"

### Documentation Triggers
> ✅ "After implementing, remind me to add a Google-style docstring and update `docs/source/api/`"

---

## 13. Maintenance Checklist

Before every PR:
- [ ] `uv run mypy src/` — zero new type errors
- [ ] `uv run black src/` — code formatted
- [ ] No `print()` in non-`__main__` code paths
- [ ] All new `Settings` fields have a matching entry in `.env.example`
- [ ] New modules have a docstring on the class and all public methods
- [ ] `pyproject.toml` version bumped if releasing docs
- [ ] Docs build passes: `cd docs && uv run sphinx-build -b html source/ build/html/dev`
