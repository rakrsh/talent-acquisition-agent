"""HTTP Server - 12-Factor App Factor VII: Port Binding."""

import os
from contextlib import asynccontextmanager
from typing import List, Optional

import uvicorn
from config import logger
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from modules.job_search import JobSearcher
from modules.tracker import ApplicationTracker
from pydantic import BaseModel
from settings import get_settings


# =============================================================================
# FastAPI App
# =============================================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Factor IX: Disposability - clean startup/shutdown."""
    logger.info("Job Agent starting up")
    yield
    logger.info("Job Agent shutting down")


app = FastAPI(
    title="Job Agent API",
    description="Talent Acquisition Agent - 12-Factor App compliant",
    version="1.1.0",
    lifespan=lifespan,
)

# Mount static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
if not os.path.exists(static_dir):
    os.makedirs(static_dir)

app.mount("/static", StaticFiles(directory=static_dir), name="static")


# =============================================================================
# Pydantic Models
# =============================================================================
class JobResponse(BaseModel):
    title: str
    company: str
    location: str
    url: str
    source: str
    posted_date: Optional[str] = None


class SearchRequest(BaseModel):
    tags: Optional[List[str]] = None


class ApplicationRequest(BaseModel):
    title: str
    company: str
    location: str
    url: str
    source: str


# =============================================================================
# Routes
# =============================================================================
@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve the Web UI - Factor VII: Port Binding."""
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        with open(index_path, encoding="utf-8") as f:
            return f.read()
    return """
    <html>
        <head><title>Job Agent</title></head>
        <body style="font-family: sans-serif; background: #0f172a; color: white; display: flex; align-items: center; justify-content: center; height: 100vh;">
            <div style="text-align: center;">
                <h1>Job Agent UI</h1>
                <p>Initializing UI components...</p>
                <progress></progress>
            </div>
            <script>setTimeout(() => window.location.reload(), 2000);</script>
        </body>
    </html>
    """


@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/jobs")
async def search_jobs():
    """Search for jobs - triggers job search pipeline."""
    settings = get_settings()
    searcher = JobSearcher()

    jobs = await searcher.search_all()

    return {
        "count": len(jobs),
        "jobs": [
            JobResponse(
                title=j.title,
                company=j.company,
                location=j.location,
                url=j.url,
                source=j.source,
                posted_date=j.posted_date,
            )
            for j in jobs[: settings.max_jobs_per_search]
        ],
    }


@app.get("/applications")
async def get_applications():
    """Get all tracked applications."""
    tracker = ApplicationTracker()
    apps = tracker.get_applications()

    return {"count": len(apps), "summary": tracker.get_summary(), "applications": apps}


@app.post("/applications")
async def add_application(app: ApplicationRequest):
    """Record a new job application."""
    tracker = ApplicationTracker()

    # Create a job-like object
    class TempJob:
        def __init__(self, title, company, location, url, source):
            self.title = title
            self.company = company
            self.location = location
            self.url = url
            self.source = source

    job = TempJob(
        title=app.title,
        company=app.company,
        location=app.location,
        url=app.url,
        source=app.source,
    )

    success = tracker.add_application(job)

    if success:
        return {"status": "recorded", "url": app.url}
    raise HTTPException(status_code=409, detail="Already applied")


@app.get("/applications/{url}/status")
async def get_application_status(url: str):
    """Get status of a specific application."""
    tracker = ApplicationTracker()
    apps = tracker.get_applications()

    for app in apps:
        if app.url == url:
            return {
                "url": url,
                "status": app.status,
                "applied_date": app.applied_date,
                "notes": app.notes,
            }

    raise HTTPException(status_code=404, detail="Application not found")


@app.patch("/applications/{url}/status")
async def update_application_status(url: str, status: str, notes: str = ""):
    """Update application status."""
    tracker = ApplicationTracker()
    success = tracker.update_status(url, status, notes)

    if success:
        return {"status": "updated", "url": url, "new_status": status}
    raise HTTPException(status_code=404, detail="Application not found")


# =============================================================================
# Factor VII: Port Binding - Run as HTTP service
# =============================================================================
def run_server():
    """Run the HTTP server."""
    settings = get_settings()
    logger.info(f"Starting HTTP server on {settings.http_host}:{settings.http_port}")

    uvicorn.run(
        "server:app",
        host=settings.http_host,
        port=settings.http_port,
        log_level=settings.log_level.lower(),
    )


if __name__ == "__main__":
    run_server()
