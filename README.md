# Job Agent - Talent Acquisition Agent

> Open Source Agentic AI Job Search Engine with 12-Factor App compliance

[![Python 3.12+](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![12-Factor App](https://img.shields.io/badge/12-Factor%20App-Compliant-green.svg)](https://12factor.net/)

Job Agent is an automated job search and application tracking system that searches multiple job boards, notifies you of new opportunities, and tracks all your applications in a local database.

## Features

- 🔍 **Multi-source Job Search** - Searches Remote OK, LinkedIn, Indeed
- 📧 **Email Notifications** - Get alerted when new jobs match your criteria
- 📱 **SMS Notifications** - Twilio integration for text alerts
- 📁 **Application Tracking** - Local JSON database of all applications
- 🤖 **Auto-Apply (Beta)** - Automatically apply to matching jobs
- 🌐 **HTTP API** - Run as a REST API service (FastAPI)
- 📋 **12-Factor App** - Cloud-native, production-ready

## Quick Start

### 1. Clone and Install

```bash
# Clone the repository
git clone https://github.com/yourusername/talent-acquisition-agent.git
cd talent-acquisition-agent

# Install dependencies
uv sync
```

### 2. Configure

Copy the example environment file and fill in your values:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
# Email notifications
SENDER_EMAIL=your.email@gmail.com
SENDER_PASSWORD=your-gmail-app-password
RECIPIENT_EMAIL=your@email.com

# SMS notifications (optional)
TWILIO_SID=your_twilio_sid
TWILIO_TOKEN=your_twilio_token
TWILIO_PHONE=+1234567890
RECIPIENT_PHONE=+0987654321
```

### 3. Define Search Criteria

Edit `input/search_criteria.json` to set your job search terms:

```json
{
  "search_terms": [
    {
      "role": "python",
      "keywords": ["backend", "api"],
      "locations": ["remote"],
      "job_types": ["full-time"]
    }
  ]
}
```

### 4. Run

```bash
# CLI mode
uv run .\src\main.py

# HTTP server mode
uv run .\src\server.py
```

## Configuration

All configuration is managed via environment variables (Factor III: Config):

| Variable | Description | Default |
|----------|-------------|---------|
| `ENV_MODE` | Environment mode | `development` |
| `LOG_LEVEL` | Logging level | `INFO` |
| `REMOTE_OK_ENABLED` | Enable Remote OK search | `true` |
| `MAX_JOBS_PER_SEARCH` | Max jobs to fetch | `20` |
| `AUTO_APPLY_ENABLED` | Enable auto-apply | `false` |
| `HTTP_PORT` | HTTP server port | `8080` |

## Project Structure

```
talent-acquisition-agent/
├── .env.example          # Environment template
├── pyproject.toml        # Dependencies
├── data/                 # Application data
│   └── applications.json
├── input/
│   └── search_criteria.json
├── docs/                 # Sphinx documentation
└── src/
    ├── config.py         # Logging configuration
    ├── settings.py       # Environment settings
    ├── main.py           # CLI entry point
    ├── server.py         # HTTP API server
    └── modules/
        ├── job_search.py     # Job search module
        ├── notifications.py  # Email/SMS notifications
        └── tracker.py        # Application tracker
```

## 12-Factor App Compliance

This application follows the [12-Factor](https://12factor.net/) methodology:

| Factor | Implementation |
|--------|---------------|
| I. Codebase | Single git repo |
| II. Dependencies | Explicit in `pyproject.toml` |
| III. Config | Environment variables |
| IV. Backing Services | External APIs |
| V. Build/Release/Run | `uv run` |
| VI. Processes | Stateless, async |
| VII. Port Binding | FastAPI HTTP server |
| VIII. Concurrency | `asyncio.gather` |
| IX. Disposability | Fast startup |
| X. Dev/Prod Parity | Same environment |
| XI. Logs | Structured logging |
| XII. Admin Processes | Separate modules |

## API Endpoints (FastAPI)

When running in server mode:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Health check |
| `/health` | GET | Service health |
| `/jobs` | GET | Search jobs |
| `/applications` | GET | List applications |
| `/applications` | POST | Add application |
| `/applications/{url}/status` | GET | Get application status |
| `/applications/{url}/status` | PATCH | Update status |

## Development

```bash
# Run tests
uv run pytest

# Format code
uv run black src/

# Type check
uv run mypy src/
```

## License

MIT License - see [LICENSE](LICENSE) for details.

## Contributing

Contributions are welcome! Please open an issue or submit a PR.