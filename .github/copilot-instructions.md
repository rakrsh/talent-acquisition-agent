# GitHub Copilot Instructions — Talent Acquisition Agent (Microservices Edition)

> These instructions govern how Copilot (and all AI assistants) should reason about,
> generate, and review code in this repository. Follow them in every suggestion.

---

## 1. Project Identity

| Property | Value |
|---|---|
| **Name** | `talent-acquisition-agent` (Job Agent) |
| **Architecture** | Dockerized Microservices |
| **Language** | Python 3.12+ (Backend), Next.js 14+ (Frontend) |
| **Package Manager** | `uv` (Python), `npm` (Frontend) |
| **Entry Points** | `services/api/app.py` (Orchestrator), `services/search/app.py` (Scraper), `services/web/` (Next.js) |
| **Config Pattern** | 12-Factor App — all config from environment variables |
| **Async Runtime** | `asyncio` — all backend I/O is async |
| **HTTP Framework** | FastAPI (Backend) |

---

## 2. Architecture Invariants

These rules reflect the 12-Factor methodology baked into this project. **Never violate them.**

### Factor III — Config
- All backend configuration lives in `settings.py` within each service folder via `pydantic-settings`.
- Frontend config uses `NEXT_PUBLIC_` environment variables.
- **Never hardcode** API keys, hostnames, ports, or paths.

### Factor XI — Logs
- Backend: Always use the project logger: `from config import logger`
- Frontend: Use `console.log` for debugging in dev, but prefer a logging service in production.
- **Never use `print()`** in production backend code paths.

### Factor VI — Processes
- All services must be stateless.
- Shared state belongs in the configured `DATABASE_URL` (SQLite/PostgreSQL) or `mongodb`.

### Factor IV — Backing Services
- External services (job boards, Twilio, SMTP) are treated as attached resources.
- The `api` service communicates with the `search` service via HTTP.

---

## 3. Code Style & Conventions

### Python Style (Backend)
- Use **dataclasses** for data containers.
- Use **Pydantic `BaseModel`** for API request/response schemas.
- Type-annotate every function signature.
- Imports: Use service-local imports (e.g. `from modules.job_search import JobSearcher` within `services/search`).

### TypeScript Style (Frontend)
- Use **Functional Components** with Hooks (`useState`, `useEffect`).
- Use **TypeScript interfaces** for all data models (mirrored from backend Pydantic models).
- Styling: Use **Vanilla CSS** or **CSS Modules** for custom designs. Avoid Tailwind unless explicitly requested.

---

## 4. Service Responsibilities

```
services/
├── api/            → Orchestration, tracking, and notifications.
│   ├── app.py      → Main gateway.
│   └── modules/    → tracker.py, notifications.py.
├── search/         → Job board scraping service.
│   ├── app.py      → Search API.
│   └── modules/    → job_search.py, auth.py.
└── web/            → Next.js frontend dashboard.
```

---

## 5. Adding New Features

- **New Job Board**: Add to `services/search/modules/job_search.py` and update `settings.py` in the search service.
- **New UI Feature**: Update `services/web/src/app/page.tsx` and ensure the `api` service has the necessary endpoint.
- **New Data Point**: Update Pydantic models in both `api` and `search`, and the TypeScript interface in `web`.

---

## 6. Testing Guidelines

- **Backend**: Use `pytest`. Tests are located in the root `tests/` directory, structured by service (e.g., `tests/services/api`).
- **Frontend**: Use `jest` or `vitest` for component testing.
- **Integration**: Use `docker-compose` to spin up the full stack for end-to-end testing.

---

## 7. Documentation Standards

- **Backend**: Google-style docstrings.
- **Frontend**: JSDoc comments for complex components and hooks.
- **System**: Update `AGENTS.md` for any architecture-level changes.

---

## 8. Security Rules

- **Never log secrets** or PII.
- All backend routes must handle `CORS` correctly (configured in `api/app.py`).
- Use `.env.example` to document required variables across all services.
- Always use `aiohttp` for backend-to-backend communication.
