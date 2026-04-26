"""Job search module - scrapes job listings from various sources."""

import asyncio
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

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

    # Job board base URLs and their search patterns
    JOB_BOARDS = {
        "remote-ok": {
            "base_url": "https://remoteok.com/api",
            "query_param": "tag",
            "enabled_setting": "remote_ok_enabled",
        },
        "we-work-remotely": {
            "base_url": "https://weworkremotely.com/api",
            "query_param": "tag",
            "enabled_setting": "we_work_remotely_enabled",
        },
        "jooble": {
            "base_url": "https://jooble.org/api",
            "query_param": "search",
            "enabled_setting": "jooble_enabled",
            "uses_post": True,
        },
        "glassdoor": {
            "base_url": "https://www.glassdoor.com/api-web",
            "query_param": "keyword",
            "enabled_setting": "glassdoor_enabled",
        },
        "monster": {
            "base_url": "https://www.monster.com/api/v1",
            "query_param": "q",
            "enabled_setting": "monster_enabled",
        },
        "careerjet": {
            "base_url": "https://www.careerjet.com/partners/api/v1",
            "query_param": "search",
            "enabled_setting": "careerjet_enabled",
        },
        "simplyhired": {
            "base_url": "https://www.simplyhired.com/api/v1",
            "query_param": "q",
            "enabled_setting": "simplyhired_enabled",
        },
        "ziprecruiter": {
            "base_url": "https://api.ziprecruiter.com/jobs/v1",
            "query_param": "search",
            "enabled_setting": "ziprecruiter_enabled",
        },
        "lever": {
            "base_url": "https://api.lever.co/v0/postings",
            "query_param": "company",
            "enabled_setting": "lever_enabled",
            "is_company_listing": True,
        },
        "ashby": {
            "base_url": "https://api.ashbyhq.com/postings",
            "query_param": "company",
            "enabled_setting": "ashby_enabled",
            "is_company_listing": True,
        },
    }

    def __init__(self, config_path: Optional[str] = None):
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
        """Search all configured sources in parallel."""
        settings = get_settings()
        all_jobs = []
        tasks = []

        # Build task list based on enabled job boards
        if settings.remote_ok_enabled:
            tasks.append(self._search_remote_ok())
        if settings.remotive_enabled:
            tasks.append(self._search_remotive())
        if settings.we_work_remotely_enabled:
            tasks.append(self._search_we_work_remotely())
        if settings.jooble_enabled:
            tasks.append(self._search_jooble())
        if settings.glassdoor_enabled:
            tasks.append(self._search_glassdoor())
        if settings.monster_enabled:
            tasks.append(self._search_monster())
        if settings.careerjet_enabled:
            tasks.append(self._search_careerjet())
        if settings.simplyhired_enabled:
            tasks.append(self._search_simplyhired())
        if settings.ziprecruiter_enabled:
            tasks.append(self._search_ziprecruiter())
        if settings.lever_enabled:
            tasks.append(self._search_lever())
        if settings.ashby_enabled:
            tasks.append(self._search_ashby())

        if not tasks:
            logger.warning("No job boards enabled. Enable at least one in settings.")
            return []

        logger.info(f"Searching {len(tasks)} job boards...")

        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if isinstance(result, list):
                all_jobs.extend(result)
            elif isinstance(result, Exception):
                logger.error(f"Job search failed: {result}")

        # Deduplicate by URL
        seen_urls = set()
        unique_jobs = []
        for job in all_jobs:
            if job.url not in seen_urls:
                seen_urls.add(job.url)
                unique_jobs.append(job)

        self.jobs = unique_jobs
        logger.info(f"Found {len(unique_jobs)} unique jobs across all sources")
        return unique_jobs

    # =========================================================================
    # Job Board Search Methods
    # =========================================================================

    async def _search_remote_ok(self) -> list[Job]:
        """Search Remote OK job board."""
        jobs = []
        search_terms = self.search_config.get("search_terms", [])

        for term in search_terms:
            role = term.get("role", "")
            tag = role.lower().replace(" ", "-")
            url = f"https://remoteok.com/api?tag={tag}"

            try:
                async with aiohttp.ClientSession() as session, session.get(
                    url, timeout=10
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        for item in data[1:21]:  # Skip first item (legal notice)
                            if (
                                isinstance(item, dict)
                                and item.get("company")
                                and item.get("position")
                            ):
                                jobs.append(
                                    Job(
                                        title=item.get("position", ""),
                                        company=item.get("company", ""),
                                        location=item.get("location", "Remote"),
                                        url=item.get("url", "")
                                        or f"https://remoteok.com{item.get('url', '')}",
                                        source="remote-ok",
                                        posted_date=item.get("date", ""),
                                        search_term=role,
                                    )
                                )
            except asyncio.TimeoutError:
                logger.warning(f"Remote OK timeout for role: {role}")
            except Exception as e:
                logger.error(f"Remote OK search error for '{role}': {e}")

        return jobs

    async def _search_remotive(self) -> list[Job]:
        """Search Remotive API - reliable remote job board."""
        jobs = []
        search_terms = self.search_config.get("search_terms", [])

        # Map roles to Remotive categories
        category_map = {
            "python": "software-dev",
            "devops": "devops",
            "site reliability engineer": "devops",
            "javascript": "frontend",
            "ai": "data",
        }

        for term in search_terms:
            role = term.get("role", "")
            category = category_map.get(role.lower(), "software-dev")
            url = f"https://remotive.com/api/remote-jobs?category={category}&limit=20"

            try:
                async with aiohttp.ClientSession() as session, session.get(
                    url, timeout=15
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        for item in data.get("jobs", [])[:20]:
                            jobs.append(
                                Job(
                                    title=item.get("title", ""),
                                    company=item.get("company", ""),
                                    location=item.get(
                                        "candidate_required_location", "Remote"
                                    ),
                                    url=item.get("url", ""),
                                    source="remotive",
                                    posted_date=item.get("published_at", ""),
                                    salary=item.get("salary", ""),
                                    search_term=role,
                                )
                            )
            except asyncio.TimeoutError:
                logger.warning(f"Remotive timeout for role: {role}")
            except Exception as e:
                logger.error(f"Remotive search error for '{role}': {e}")

        return jobs

    async def _search_we_work_remotely(self) -> list[Job]:
        """Search We Work Remotely job board."""
        jobs = []
        search_terms = self.search_config.get("search_terms", [])

        for term in search_terms:
            role = term.get("role", "")
            tag = role.lower().replace(" ", "-").replace(".", "")
            url = f"https://weworkremotely.com/api/tags/{tag}/jobs.json"

            try:
                async with aiohttp.ClientSession() as session, session.get(
                    url, timeout=15
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        for item in data.get("jobs", [])[:20]:
                            jobs.append(
                                Job(
                                    title=item.get("title", ""),
                                    company=item.get("company", {}).get("name", ""),
                                    location=item.get("location", "Remote"),
                                    url=f"https://weworkremotely.com{item.get('url', '')}",
                                    source="we-work-remotely",
                                    posted_date=item.get("published_at", ""),
                                    search_term=role,
                                )
                            )
            except asyncio.TimeoutError:
                logger.warning(f"We Work Remotely timeout for role: {role}")
            except Exception as e:
                logger.error(f"We Work Remotely search error for '{role}': {e}")

        return jobs

    async def _search_jooble(self) -> list[Job]:
        """Search Jooble job board (global job search)."""
        jobs = []
        search_terms = self.search_config.get("search_terms", [])

        # Jooble API key would be needed for full API access
        # Using their public search as fallback
        for term in search_terms:
            role = term.get("role", "")
            keywords = term.get("keywords", [])
            search_query = role
            if keywords:
                search_query += " " + " ".join(keywords[:2])

            # Jooble public search endpoint
            url = f"https://jooble.org/jobs/{search_query.replace(' ', '-')}"

            try:
                async with aiohttp.ClientSession() as session, session.get(
                    url, timeout=15, headers={"User-Agent": "Mozilla/5.0"}
                ) as resp:
                    if resp.status == 200:
                        html = await resp.text()
                        # Parse job listings from HTML (simplified)
                        job_pattern = re.compile(
                            r'<a[^>]+href="(/job/[^"]+)"[^>]*>([^<]+)</a>'
                        )
                        for match in job_pattern.finditer(html)[:20]:
                            jobs.append(
                                Job(
                                    title=match.group(2).strip(),
                                    company="",
                                    location="",
                                    url=f"https://jooble.org{match.group(1)}",
                                    source="jooble",
                                    search_term=role,
                                )
                            )
            except asyncio.TimeoutError:
                logger.warning(f"Jooble timeout for role: {role}")
            except Exception as e:
                logger.error(f"Jooble search error for '{role}': {e}")

        return jobs

    async def _search_glassdoor(self) -> list[Job]:
        """Search Glassdoor job board."""
        jobs = []
        search_terms = self.search_config.get("search_terms", [])

        for term in search_terms:
            role = term.get("role", "")
            keywords = " ".join(term.get("keywords", [])[:2])
            search_query = f"{role} {keywords}".strip()

            url = f"https://www.glassdoor.com/Reviews/jobs.htm?sc.keyword={search_query.replace(' ', '%20')}"

            try:
                async with aiohttp.ClientSession() as session, session.get(
                    url, timeout=15, headers={"User-Agent": "Mozilla/5.0"}
                ) as resp:
                    if resp.status == 200:
                        # Glassdoor requires more complex parsing
                        # Placeholder - would need Selenium for full implementation
                        logger.debug(f"Glassdoor search for: {search_query}")
            except Exception as e:
                logger.error(f"Glassdoor search error for '{role}': {e}")

        return jobs

    async def _search_monster(self) -> list[Job]:
        """Search Monster job board."""
        jobs = []
        search_terms = self.search_config.get("search_terms", [])

        for term in search_terms:
            role = term.get("role", "")
            url = f"https://www.monster.com/jobs/search/?q={role.replace(' ', '+')}"

            try:
                async with aiohttp.ClientSession() as session, session.get(
                    url, timeout=15, headers={"User-Agent": "Mozilla/5.0"}
                ) as resp:
                    if resp.status == 200:
                        logger.debug(f"Monster search for: {role}")
            except Exception as e:
                logger.error(f"Monster search error for '{role}': {e}")

        return jobs

    async def _search_careerjet(self) -> list[Job]:
        """Search CareerJet job board."""
        jobs = []
        search_terms = self.search_config.get("search_terms", [])

        for term in search_terms:
            role = term.get("role", "")
            url = f"https://www.careerjet.com/search/jobs?k={role.replace(' ', '+')}"

            try:
                async with aiohttp.ClientSession() as session, session.get(
                    url, timeout=15, headers={"User-Agent": "Mozilla/5.0"}
                ) as resp:
                    if resp.status == 200:
                        logger.debug(f"CareerJet search for: {role}")
            except Exception as e:
                logger.error(f"CareerJet search error for '{role}': {e}")

        return jobs

    async def _search_simplyhired(self) -> list[Job]:
        """Search SimplyHired job board."""
        jobs = []
        search_terms = self.search_config.get("search_terms", [])

        for term in search_terms:
            role = term.get("role", "")
            url = f"https://www.simplyhired.com/search?q={role.replace(' ', '+')}"

            try:
                async with aiohttp.ClientSession() as session, session.get(
                    url, timeout=15, headers={"User-Agent": "Mozilla/5.0"}
                ) as resp:
                    if resp.status == 200:
                        logger.debug(f"SimplyHired search for: {role}")
            except Exception as e:
                logger.error(f"SimplyHired search error for '{role}': {e}")

        return jobs

    async def _search_ziprecruiter(self) -> list[Job]:
        """Search ZipRecruiter job board."""
        jobs = []
        search_terms = self.search_config.get("search_terms", [])

        for term in search_terms:
            role = term.get("role", "")
            url = f"https://www.ziprecruiter.com/jobs/k-{role.replace(' ', '-')}"

            try:
                async with aiohttp.ClientSession() as session, session.get(
                    url, timeout=15, headers={"User-Agent": "Mozilla/5.0"}
                ) as resp:
                    if resp.status == 200:
                        logger.debug(f"ZipRecruiter search for: {role}")
            except Exception as e:
                logger.error(f"ZipRecruiter search error for '{role}': {e}")

        return jobs

    async def _search_lever(self) -> list[Job]:
        """Search Lever job board (aggregates company postings)."""
        jobs = []
        search_terms = self.search_config.get("search_terms", [])

        # Common companies on Lever (would need config for company list)
        lever_companies = [
            "stripe",
            "airbnb",
            "notion",
            "figma",
            "twilio",
            "datadog",
            "snowflake",
            "cloudflare",
            "elastic",
            "gitlab",
        ]

        for company in lever_companies[:5]:  # Limit to avoid rate limits
            url = f"https://api.lever.co/v0/postings/{company}?mode=json"

            try:
                async with aiohttp.ClientSession() as session, session.get(
                    url, timeout=15
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        for item in data[:10]:
                            jobs.append(
                                Job(
                                    title=item.get("text", ""),
                                    company=company.title(),
                                    location=item.get("location", ""),
                                    url=item.get("applyUrl", ""),
                                    source="lever",
                                    posted_date=item.get("createdAt", ""),
                                    search_term=f"lever-{company}",
                                )
                            )
            except Exception as e:
                logger.debug(f"Lever search error for '{company}': {e}")

        return jobs

    async def _search_ashby(self) -> list[Job]:
        """Search Ashby job board (aggregates company postings)."""
        jobs = []
        search_terms = self.search_config.get("search_terms", [])

        # Common companies on Ashby (would need config for company list)
        ashby_companies = ["linear", "cal.com", "resend", "raycast", "polymarket"]

        for company in ashby_companies[:5]:  # Limit to avoid rate limits
            url = f"https://api.ashbyhq.com/postings?companySlug={company}"

            try:
                async with aiohttp.ClientSession() as session, session.get(
                    url, timeout=15
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        for item in data.get("jobs", [])[:10]:
                            jobs.append(
                                Job(
                                    title=item.get("title", ""),
                                    company=company.title(),
                                    location=item.get("location", {}).get("city", ""),
                                    url=item.get("applyUrl", ""),
                                    source="ashby",
                                    posted_date=item.get("publishedAt", ""),
                                    search_term=f"ashby-{company}",
                                )
                            )
            except Exception as e:
                logger.debug(f"Ashby search error for '{company}': {e}")

        return jobs

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
