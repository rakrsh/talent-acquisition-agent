"""Search Service - Handles job scraping across all tiers."""

from contextlib import asynccontextmanager
from typing import Optional

import uvicorn
from config import logger
from fastapi import FastAPI, HTTPException
from modules.job_search import JobSearcher
from pydantic import BaseModel
from settings import get_settings


# =============================================================================
# FastAPI App
# =============================================================================
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Search Service starting up")
    yield
    logger.info("Search Service shutting down")


app = FastAPI(
    title="Job Search Service",
    description="Dedicated service for scraping job boards",
    version="0.1.dev0",
    lifespan=lifespan,
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


# =============================================================================
# Routes
# =============================================================================
@app.get("/health")
async def health():
    return {"status": "healthy", "service": "search-service"}


@app.get("/search")
async def search_jobs():
    """Trigger job search pipeline."""
    settings = get_settings()
    searcher = JobSearcher()

    try:
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
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail="Search failed") from e


def run_server():
    settings = get_settings()
    # Use a different port for search service
    port = settings.search_service_port
    uvicorn.run("app:app", host="0.0.0.0", port=port, log_level="info")


if __name__ == "__main__":
    run_server()
