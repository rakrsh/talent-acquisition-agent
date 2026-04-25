"""Job search module - scrapes job listings from various sources."""
import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, asdict
import aiohttp

from config import logger
from settings import get_settings


@dataclass
class Job:
    """Job listing data structure."""
    title: str
    company: str
    location: str
    url: str
    source: str  # linkedin, indeed, remote-ok, etc.
    posted_date: Optional[str] = None
    salary: Optional[str] = None
    description: Optional[str] = None
    applied: bool = False
    applied_date: Optional[str] = None
    search_term: str = ""


class JobSearcher:
    """Searches job boards for new listings."""
    
    def __init__(self, config_path: str = None):
        settings = get_settings()
        self.config_path = Path(config_path or settings.config_file_path)
        self.search_config = self._load_config()
        self.jobs: list[Job] = []
    
    def _load_config(self) -> dict:
        """Load search criteria from JSON file."""
        if self.config_path.exists():
            with open(self.config_path) as f:
                return json.load(f)
        return {"search_terms": []}
    
    async def search_all(self) -> list[Job]:
        """Search all configured sources."""
        all_jobs = []
        
        # Run searches in parallel
        tasks = [
            self._search_remote_ok(),
            self._search_indeed(),
        ]
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, list):
                all_jobs.extend(result)
        
        self.jobs = all_jobs
        return all_jobs
    
    async def _search_remote_ok(self) -> list[Job]:
        """Search Remote OK job board."""
        jobs = []
        search_terms = self.search_config.get("search_terms", [])
        
        for term in search_terms:
            role = term.get("role", "")
            tag = role.lower().replace(' ', '-')
            url = f"https://remoteok.com/api?tag={tag}"
            
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, timeout=10) as resp:
                        if resp.status == 200:
                            data = await resp.json()
                            for item in data[1:21]:  # Skip first item (legal notice)
                                if isinstance(item, dict) and item.get("company") and item.get("position"):
                                    jobs.append(Job(
                                        title=item.get("position", ""),
                                        company=item.get("company", ""),
                                        location=item.get("location", "Remote"),
                                        url=item.get("url", ""),
                                        source="remote-ok",
                                        posted_date=item.get("date", ""),
                                        search_term=role
                                    ))
            except Exception as e:
                print(f"Remote OK search error for '{role}': {e}")
        
        return jobs
    
    async def _search_indeed(self) -> list[Job]:
        """Search Indeed (requires more complex scraping)."""
        # Indeed requires more sophisticated scraping
        # Placeholder for now - would need Selenium or similar
        return []
    
    async def _search_linkedin(self) -> list[Job]:
        """Search LinkedIn (requires authentication)."""
        # LinkedIn has strict anti-scraping measures
        # Would need LinkedIn API access or Selenium
        return []
    
    def filter_new_jobs(self, existing_jobs: list[Job]) -> list[Job]:
        """Filter out jobs we've already seen."""
        existing_urls = {job.url for job in existing_jobs}
        return [job for job in self.jobs if job.url not in existing_urls]


# Quick test
if __name__ == "__main__":
    async def test():
        searcher = JobSearcher()
        jobs = await searcher.search_all()
        print(f"Found {len(jobs)} jobs")
        for job in jobs[:5]:
            print(f"  - {job.title} @ {job.company} ({job.source})")
    
    asyncio.run(test())