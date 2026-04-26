# Job Agent - Talent Acquisition Agent

> Open Source Agentic AI Job Search Engine with 12-Factor App compliance

[![Python 3.12+](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![Next.js 14](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![12-Factor App](https://img.shields.io/badge/12-Factor%20App-Compliant-green.svg)](https://12factor.net/)

Job Agent is a microservices-based automated job search and application tracking system. It searches multiple job boards, notifies you of new opportunities, and tracks all your applications.

## 🚀 Architecture

The system is split into three core microservices:

1.  **Search Service** (`services/search`): Specialized scraper for 10+ job boards.
2.  **API Service** (`services/api`): Orchestrator, application tracker, and notification gateway.
3.  **Web UI** (`services/web`): Modern Next.js dashboard for managing your job hunt.

## ✨ Features

- 🔍 **Multi-source Job Search** - Searches Remote OK, LinkedIn, Indeed, and 10+ others.
- 📧 **Automated Notifications** - Email and SMS alerts for new matches.
- 📁 **Application Tracking** - Kanban board to manage your job pipeline.
- 🌐 **Modern Web UI** - Real-time dashboard with search and stats.
- 🐳 **Dockerized** - Easy deployment with Docker Compose.
- 📋 **12-Factor App** - Production-ready, cloud-native architecture.

## 🛠️ Quick Start

### 1. Clone and Configure

```bash
git clone https://github.com/yourusername/talent-acquisition-agent.git
cd talent-acquisition-agent

# Setup environment
cp .env.example .env
```

### 2. Run with Docker Compose

The easiest way to run the entire stack is using Docker:

```bash
docker-compose up --build
```

Access the components at:
- **Web UI**: [http://localhost:3002](http://localhost:3002)
- **API Gateway**: [http://localhost:8080](http://localhost:8080)
- **Search Service**: [http://localhost:8081](http://localhost:8081)
- **Grafana**: [http://localhost:3001](http://localhost:3001)

## 📦 Project Structure

```
talent-acquisition-agent/
├── services/
│   ├── api/          # FastAPI Orchestrator & Tracker
│   ├── search/       # FastAPI Job Scraper
│   └── web/          # Next.js Frontend
├── docker-compose.yml # Service orchestration
├── input/            # Search criteria configuration
├── data/             # Persistent application data
└── docs/             # Sphinx documentation
```

## 📋 API Endpoints

| Service | Endpoint | Description |
|---------|----------|-------------|
| API | `/jobs` | Trigger search (proxies to Search service) |
| API | `/applications` | List/Add applications |
| Search | `/search` | Low-level scraping endpoint |

## 🧪 Development & Testing

You can still run services locally for development:

```bash
# Start API Service
cd services/api
uv run python app.py

# Start Search Service
cd services/search
uv run python app.py

# Start Web UI
cd services/web
npm install
npm run dev
```

## 📜 License

MIT License - see [LICENSE](LICENSE) for details.
