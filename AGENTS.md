# AGENTS.md

## Purpose
This document defines the agents in the `talent-acquisition-agent` system, their responsibilities, and how they interact.  
It complements `copilot-instructions.md` by focusing on system-level agents rather than coding conventions.

---

## Agent Roles

### 1. Job Search Agent
- **Responsibility**: Fetch job listings from external boards (Remote OK, Indeed, LinkedIn, etc.).
- **12-Factor Alignment**:
  - Treat external boards as backing services (Factor IV).
  - Stateless scrapers; failures isolated per source.
  - Configurable via environment flags (`*_ENABLED`).

### 2. Application Tracker Agent
- **Responsibility**: Manage applications state (`applications.json` or database).
- **12-Factor Alignment**:
  - Processes are stateless; persistence handled externally.
  - Config-driven database URL (`DATABASE_URL`).

### 3. Notification Agent
- **Responsibility**: Send alerts via email/SMS (SMTP, Twilio).
- **12-Factor Alignment**:
  - Config from environment (`SMTP_HOST`, `TWILIO_TOKEN`).
  - Logs events, not print statements.
  - Swappable backing services.

### 4. Configuration Agent
- **Responsibility**: Centralize environment variables via `pydantic-settings`.
- **12-Factor Alignment**:
  - Factor III — Config strictly from environment.
  - `.env` ignored in VCS; `.env.example` documents required fields.

### 5. Logging Agent
- **Responsibility**: Unified JSON logging in production, human-readable in dev.
- **12-Factor Alignment**:
  - Factor XI — Logs as event streams.
  - No `print()` in production paths.

### 6. Runtime Agent
- **Responsibility**: Async orchestration (`asyncio`, FastAPI).
- **12-Factor Alignment**:
  - Factor VI — Processes are stateless and disposable.
  - Scale horizontally via process model.

### 7. Documentation Agent
- **Responsibility**: Maintain Sphinx docs (`docs/source/`), auto-deployed to GitHub Pages.
- **12-Factor Alignment**:
  - Docs treated as code, versioned alongside releases.
  - Every new feature requires doc updates.

---

## Interaction Model
- Agents communicate via **well-defined interfaces** (CLI, HTTP API, or module calls).
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
