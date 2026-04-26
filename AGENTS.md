# AGENTS.md

## Purpose
This document defines the agents in the `talent-acquisition-agent` system, their responsibilities, and how they interact.
It complements `copilot-instructions.md` by focusing on system-level agents rather than coding conventions.

---

## Agent Roles

### 1. Job Search Agent
- **Responsibility**: Fetch job listings from external boards across five source tiers.
- **Source Tiers**:
  | Tier | Sources | Auth |
  |------|---------|------|
  | 1 – Free public JSON APIs | RemoteOK, Remotive, Arbeitnow, Himalayas, Jobicy, The Muse | None |
  | 2 – RSS feeds | We Work Remotely | None |
  | 3 – API-key boards | Adzuna, Indeed (Publisher), ZipRecruiter | API key in env |
  | 4 – OAuth 2.0 | LinkedIn Jobs API | OAuth client credentials |
  | 5 – ATS aggregators | Lever, Ashby, Greenhouse | None (public API) |
- **Module**: `src/modules/job_search.py`
- **12-Factor Alignment**:
  - Treat external boards as backing services (Factor IV).
  - Stateless scrapers; failures isolated per source.
  - Configurable via environment flags (`*_ENABLED`).

### 2. Auth Agent
- **Responsibility**: Manage credentials for all job-board integrations.
  - **OAuth 2.0** – LinkedIn client-credentials flow; auto-refreshes tokens.
  - **API key / token** – Adzuna, Indeed Publisher, ZipRecruiter, GitHub; credentials injected as headers or query params.
  - **Session / cookie** – `SessionAuthenticator` base class for future browser-based boards.
- **Module**: `src/modules/auth.py`
- **Public interface**: `await get_auth_manager()` returns a singleton `AuthManager`.
- **12-Factor Alignment**:
  - Factor III — all secrets from environment, never hardcoded.
  - Credential objects passed to search methods; no global mutable state leaks.

### 3. Application Tracker Agent
- **Responsibility**: Manage applications state (`applications.json` or database).
- **Module**: `src/modules/tracker.py`
- **12-Factor Alignment**:
  - Processes are stateless; persistence handled externally.
  - Config-driven database URL (`DATABASE_URL`).

### 4. Notification Agent
- **Responsibility**: Send alerts via email/SMS (SMTP, Twilio).
- **Module**: `src/modules/notifications.py`
- **12-Factor Alignment**:
  - Config from environment (`SMTP_HOST`, `TWILIO_TOKEN`).
  - Logs events, not print statements.
  - Swappable backing services.

### 5. Configuration Agent
- **Responsibility**: Centralize environment variables via `pydantic-settings`.
- **Module**: `src/settings.py`
- **12-Factor Alignment**:
  - Factor III — Config strictly from environment.
  - `.env` ignored in VCS; `.env.example` documents required fields.

### 6. Logging Agent
- **Responsibility**: Unified JSON logging in production, human-readable in dev.
- **Module**: `src/config.py`
- **12-Factor Alignment**:
  - Factor XI — Logs as event streams.
  - No `print()` in production paths.

### 7. Runtime Agent
- **Responsibility**: Async orchestration (`asyncio`, FastAPI).
- **Module**: `src/main.py`, `src/server.py`
- **12-Factor Alignment**:
  - Factor VI — Processes are stateless and disposable.
  - Scale horizontally via process model.

### 8. Documentation Agent
- **Responsibility**: Maintain Sphinx docs (`docs/source/`), auto-deployed to GitHub Pages.
- **12-Factor Alignment**:
  - Docs treated as code, versioned alongside releases.
  - Every new feature requires doc updates.

---

## Interaction Model
- Agents communicate via **well-defined interfaces** (CLI, HTTP API, or module calls).
- The **Auth Agent** is initialised once at startup (`await get_auth_manager()`) and
  its singleton passed into the **Job Search Agent**'s `search_all()` pipeline.
- Each agent adheres to **12-Factor principles**:
  - Config in environment.
  - Dependencies declared explicitly (`uv`).
  - Logs as streams.
  - Stateless processes.
  - Backing services as attached resources.

---

## Notes
- This file is **system-facing** and should be updated whenever new agents or responsibilities are introduced.
- It resides in the **root of the repository**, alongside `README.md`, `copilot-instructions.md`, and other high-level docs.
