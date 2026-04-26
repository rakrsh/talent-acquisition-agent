"""API Gateway / Orchestrator Service."""

import os
from contextlib import asynccontextmanager
from typing import List, Optional

import aiohttp
import uvicorn
from config import logger
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from modules.tracker import ApplicationTracker
from pydantic import BaseModel
from settings import get_settings


# =============================================================================
# FastAPI App
# =============================================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("API Service starting up")
    yield
    logger.info("API Service shutting down")


app = FastAPI(
    title="Job Agent API",
    description="Orchestrator for Talent Acquisition Agent",
    version="1.1.0",
    lifespan=lifespan,
)

# Enable CORS for the Next.js frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
@app.get("/health")
async def health():
    return {"status": "healthy", "service": "api-service"}


@app.get("/jobs")
async def search_jobs():
    """Proxy request to Search Service."""
    search_url = os.getenv("SEARCH_SERVICE_URL", "http://search:8081/search")

    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(search_url) as resp:
                if resp.status == 200:
                    return await resp.json()
                else:
                    logger.error(f"Search service returned {resp.status}")
                    raise HTTPException(
                        status_code=resp.status, detail="Search service error"
                    )
        except Exception as e:
            logger.error(f"Could not connect to search service: {e}")
            raise HTTPException(
                status_code=503, detail="Search service unavailable"
            ) from e


@app.get("/applications")
async def get_applications():
    """Get all tracked applications."""
    tracker = ApplicationTracker()
    apps = tracker.get_applications()

    return {"count": len(apps), "summary": tracker.get_summary(), "applications": apps}


@app.post("/applications")
async def add_application(app_req: ApplicationRequest):
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
        title=app_req.title,
        company=app_req.company,
        location=app_req.location,
        url=app_req.url,
        source=app_req.source,
    )

    success = tracker.add_application(job)

    if success:
        return {"status": "recorded", "url": app_req.url}
    raise HTTPException(status_code=409, detail="Already applied")


@app.get("/applications/{url}/status")
async def get_application_status(url: str):
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
    tracker = ApplicationTracker()
    success = tracker.update_status(url, status, notes)

    if success:
        return {"status": "updated", "url": url, "new_status": status}
    raise HTTPException(status_code=404, detail="Application not found")


def run_server():
    settings = get_settings()
    uvicorn.run("app:app", host="0.0.0.0", port=settings.http_port, log_level="info")


if __name__ == "__main__":
    run_server()
