# AGENTS.md

## Purpose
This document defines the agents in the `talent-acquisition-agent` system, their responsibilities, and how they interact within the **microservices architecture**.
It complements `copilot-instructions.md` by focusing on system-level agents rather than coding conventions.

---

## Agent Roles

### 1. Job Search Agent
- **Responsibility**: Fetch job listings from external boards across five source tiers.
- **Source Tiers**:
  | Tier | Sources | Auth |
  |------|---------|------|
  | 1 - Free public JSON APIs | RemoteOK, Remotive, Arbeitnow, Himalayas, Jobicy, The Muse | None |
  | 2 - RSS feeds | We Work Remotely | None |
  | 3 - API-key boards | Adzuna, Indeed (Publisher), ZipRecruiter | API key in env |
  | 4 - OAuth 2.0 | LinkedIn Jobs API | OAuth client credentials |
  | 5 - ATS aggregators | Lever, Ashby, Greenhouse | None (public API) |
- **Service**: `services/search`
- **Module**: `services/search/modules/job_search.py`
- **12-Factor Alignment**:
  - Treat external boards as backing services (Factor IV).
  - Stateless scrapers; failures isolated per source.

### 2. Auth Agent
- **Responsibility**: Manage credentials for all job-board integrations.
  - **OAuth 2.0** - LinkedIn client-credentials flow; auto-refreshes tokens.
  - **API key / token** - Adzuna, Indeed Publisher, ZipRecruiter, GitHub; credentials injected as headers or query params.
- **Service**: `services/search` (used by scraper)
- **Module**: `services/search/modules/auth.py`
- **12-Factor Alignment**:
  - Factor III - all secrets from environment, never hardcoded.

### 3. Application Tracker Agent
- **Responsibility**: Manage applications state (`applications.json` or database).
- **Service**: `services/api`
- **Module**: `services/api/modules/tracker.py`
- **12-Factor Alignment**:
  - Processes are stateless; persistence handled externally.
  - Config-driven database URL (`DATABASE_URL`).

### 4. Notification Agent
- **Responsibility**: Send alerts via email/SMS (SMTP, Twilio).
- **Service**: `services/api`
- **Module**: `services/api/modules/notifications.py`
- **12-Factor Alignment**:
  - Config from environment (`SMTP_HOST`, `TWILIO_TOKEN`).
  - Swappable backing services.

### 5. Configuration Agent
- **Responsibility**: Centralize environment variables via `pydantic-settings`.
- **Module**: `settings.py` (in each service)
- **12-Factor Alignment**:
  - Factor III - Config strictly from environment.

### 6. Logging Agent
- **Responsibility**: Unified JSON logging in production, human-readable in dev.
- **Module**: `config.py` (in each service)
- **12-Factor Alignment**:
  - Factor XI - Logs as event streams.

### 7. Orchestration Agent
- **Responsibility**: Manage interactions between services.
- **Service**: `services/api`
- **Module**: `services/api/app.py` (Proxies requests to `services/search`)

### 8. Deployment Agent (DevOps)
- **Responsibility**: Standardize deployment across environments.
- **Tools**: Docker Compose, Kubernetes manifests, Helm charts, Inno Setup, Nuitka.
- **Artifacts**: `helm/job-agent`, `k8s/base`, `k8s/overlays`, `windows/setup.iss`, `JobAgentInstaller.exe`.
- **12-Factor Alignment**:
  - Factor X - Keep development, staging, and production as similar as possible.
  - Windows Support - Compiles backend services to standalone `.exe` and packages them into a native installer.

---

## Interaction Model
- **UI Service** (`services/web`) calls **API Service** (`services/api`).
- **API Service** proxies heavy search requests to **Search Service** (`services/search`).
- **Notification Agent** is triggered by **API Service** when new jobs are tracked or matched.
- Each service adheres to **12-Factor principles**:
  - Config in environment.
  - Dependencies declared explicitly.
  - Logs as streams.
  - Stateless processes.
- **Test Isolation**: Backend tests are isolated per service to avoid naming collisions (e.g., `app.py`, `config.py`). Use service-specific `PYTHONPATH` during test execution.

---

## Notes
- This file is **system-facing** and should be updated whenever new agents or responsibilities are introduced.
- It resides in the **root of the repository**, alongside `README.md`, `copilot-instructions.md`, and other high-level docs.
