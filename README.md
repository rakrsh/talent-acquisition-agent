# Job Agent - Talent Acquisition Agent

> Open Source Agentic AI Job Search Engine with 12-Factor App compliance

[![Python 3.12+](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![Next.js 14](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![12-Factor App](https://img.shields.io/badge/12-Factor%20App-Compliant-green.svg)](https://12factor.net/)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-Ready-blue.svg)](https://kubernetes.io/)
[![Helm](https://img.shields.io/badge/Helm-Support-blue.svg)](https://helm.sh/)

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
- ☸️ **Kubernetes & Helm** - Native support for K8s deployments and Helm charts.

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
├── k8s/              # Kubernetes manifests (Base + Overlays)
├── helm/             # Helm charts for automated deployment
└── docs/             # Sphinx documentation
```

## 📋 API Endpoints

| Service | Endpoint | Description |
|---------|----------|-------------|
| API | `/jobs` | Trigger search (proxies to Search service) |
| API | `/applications` | List/Add applications |
| Search | `/search` | Low-level scraping endpoint |

## 🚀 Deployment Options

### Docker Compose (Local Dev)
The easiest way to run the entire stack locally:
```bash
docker-compose up --build
```

### Kubernetes & Helm (Cloud/Production)
For production-grade deployments:
```bash
# Using Helm
helm install job-agent ./helm/job-agent --namespace job-agent --create-namespace

# Using Kustomize
kubectl apply -k k8s/overlays/prod
```
See [k8s/README.md](k8s/README.md) for detailed instructions.

### Windows Standalone (.exe)
For a native Windows experience with installation and uninstallation features:
1. Download `JobAgentInstaller.exe` from the latest GitHub Release.
2. Run the installer (requires Administrator privileges).
3. The services will be registered as Windows Services and start automatically.
4. Access the UI at [http://localhost:8080/ui](http://localhost:8080/ui).

The installer is built using **Nuitka** (Python compilation) and **Inno Setup**.


## 🛠️ Development

### Setup environment
```bash
cp .env.example .env
# Install dependencies with uv
uv sync
```

### Pre-commit Checks
We use `pre-commit` to ensure code quality. It runs Ruff, MyPy, and secret detection.
```bash
# Install hooks
uv run pre-commit install

# Run manually
uv run pre-commit run --all-files
```

### Running Services Locally
```bash
# API Service
cd services/api && uv run python app.py

# Search Service
cd services/search && uv run python app.py

# Web UI
cd services/web && npm install && npm run dev
```

## 📜 License

MIT License - see [LICENSE](LICENSE) for details.
