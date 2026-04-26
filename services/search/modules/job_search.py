"""Job search module - scrapes/queries job listings from multiple sources.

Source tiers
------------
Tier 1 - Always-on free public JSON APIs (no auth):
  remote-ok, remotive, arbeitnow, himalayas, jobicy, the-muse

Tier 2 - RSS feed (no auth):
  we-work-remotely

Tier 3 - API-key required (configure in .env):
  adzuna, indeed, ziprecruiter

Tier 4 - OAuth 2.0 (configure LinkedIn app in .env):
  linkedin

Tier 5 - ATS aggregators (company career pages, public API):
  lever, ashby, greenhouse
"""

from __future__ import annotations

import asyncio
import json
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import aiohttp
from config import logger
from settings import get_settings

from modules.auth import get_auth_manager

# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

_HEADERS = {"User-Agent": "TalentAcquisitionAgent/2.0 (+https://github.com/rakrsh)"}
_TIMEOUT = aiohttp.ClientTimeout(total=20)
_SENSITIVE_QUERY_KEYS = {"api_key", "apikey", "key", "token", "access_token", "password"}


def _redact_url_for_logging(url: str) -> str:
    try:
        parts = urlsplit(url)
        if not parts.query:
            return url
        redacted_query = []
        for k, v in parse_qsl(parts.query, keep_blank_values=True):
            if k.lower() in _SENSITIVE_QUERY_KEYS:
                redacted_query.append((k, "***REDACTED***"))
            else:
                redacted_query.append((k, v))
        return urlunsplit(
            (parts.scheme, parts.netloc, parts.path, urlencode(redacted_query), parts.fragment)
        )
    except Exception:
        return "<redacted-url>"


async def _get_json(
    session: aiohttp.ClientSession, url: str, **kwargs
) -> dict | list | None:
    try:
        async with session.get(url, timeout=_TIMEOUT, headers=_HEADERS, **kwargs) as r:
            if r.status == 200:
                return await r.json(content_type=None)
            logger.debug(f"GET {_redact_url_for_logging(url)} → {r.status}")
    except asyncio.TimeoutError:
        logger.warning(f"Timeout: {_redact_url_for_logging(url)}")
    except Exception as exc:
        logger.error(f"Error fetching {_redact_url_for_logging(url)}: {exc}")
    return None


async def _get_text(session: aiohttp.ClientSession, url: str, **kwargs) -> str | None:
    try:
        async with session.get(url, timeout=_TIMEOUT, headers=_HEADERS, **kwargs) as r:
            if r.status == 200:
                return await r.text()
            logger.debug(f"GET {_redact_url_for_logging(url)} → {r.status}")
    except asyncio.TimeoutError:
        logger.warning(f"Timeout: {_redact_url_for_logging(url)}")
    except Exception as exc:
        logger.error(f"Error fetching {_redact_url_for_logging(url)}: {exc}")
    return None


# ---------------------------------------------------------------------------
# Job dataclass
# ---------------------------------------------------------------------------


@dataclass
class Job:
    """Job listing data structure."""

    title: str
    company: str
    location: str
    url: str
    source: str
    posted_date: str | None = None
    salary: str | None = None
    description: str | None = None
    applied: bool = False
    applied_date: str | None = None
    search_term: str = ""


# ---------------------------------------------------------------------------
# JobSearcher
# ---------------------------------------------------------------------------


class JobSearcher:
    """Searches job boards for new listings."""

    def __init__(self, config_path: str | None = None):
        settings = get_settings()
        self.config_path = Path(config_path or settings.config_file_path)
        self.search_config = self._load_config()
        self.jobs: list[Job] = []

    def _load_config(self) -> dict:
        if self.config_path.exists():
            with open(self.config_path) as f:
                return json.load(f)
        return {"search_terms": []}

    @property
    def _roles(self) -> list[dict]:
        return self.search_config.get("search_terms", [])

    # ------------------------------------------------------------------
    # Orchestrator
    # ------------------------------------------------------------------

    async def search_all(self) -> list[Job]:
        """Search all configured/enabled sources in parallel."""
        settings = get_settings()
        auth = await get_auth_manager()
        tasks = []

        # Tier 1 - free public APIs
        if settings.remote_ok_enabled:
            tasks.append(self._search_remote_ok())
        if settings.remotive_enabled:
            tasks.append(self._search_remotive())
        if settings.arbeitnow_enabled:
            tasks.append(self._search_arbeitnow())
        if settings.himalayas_enabled:
            tasks.append(self._search_himalayas())
        if settings.jobicy_enabled:
            tasks.append(self._search_jobicy())
        if settings.the_muse_enabled:
            tasks.append(self._search_the_muse())

        # Tier 2 - RSS
        if settings.we_work_remotely_enabled:
            tasks.append(self._search_weworkremotely_rss())

        # Tier 3 - API key
        if settings.adzuna_enabled:
            if auth.adzuna.is_configured:
                tasks.append(self._search_adzuna(auth))
            else:
                logger.warning(
                    "Adzuna enabled but ADZUNA_APP_ID/ADZUNA_API_KEY not set."
                )
        if settings.indeed_enabled:
            if auth.indeed.is_configured:
                tasks.append(self._search_indeed(auth))
            else:
                logger.warning("Indeed enabled but INDEED_PUBLISHER_ID not set.")
        if settings.ziprecruiter_enabled:
            if auth.ziprecruiter.is_configured:
                tasks.append(self._search_ziprecruiter(auth))
            else:
                logger.warning("ZipRecruiter enabled but ZIPRECRUITER_API_KEY not set.")

        # Tier 4 - OAuth
        if settings.linkedin_enabled:
            if auth.linkedin.is_configured:
                tasks.append(self._search_linkedin(auth))
            else:
                logger.warning(
                    "LinkedIn enabled but LINKEDIN_CLIENT_ID/SECRET not set."
                )

        # Tier 5 - ATS aggregators
        if settings.lever_enabled:
            tasks.append(self._search_lever(settings))
        if settings.ashby_enabled:
            tasks.append(self._search_ashby(settings))
        if settings.greenhouse_enabled:
            tasks.append(self._search_greenhouse(settings))

        if not tasks:
            logger.warning("No job boards enabled.")
            return []

        logger.info(f"Searching {len(tasks)} job board task(s)…")
        results = await asyncio.gather(*tasks, return_exceptions=True)

        all_jobs: list[Job] = []
        for result in results:
            if isinstance(result, list):
                all_jobs.extend(result)
            elif isinstance(result, Exception):
                logger.error(f"Board search failed: {result}")

        # Deduplicate by URL
        seen: set[str] = set()
        unique: list[Job] = []
        for job in all_jobs:
            if job.url and job.url not in seen:
                seen.add(job.url)
                unique.append(job)

        self.jobs = unique
        logger.info(f"Found {len(unique)} unique jobs across all sources.")
        return unique

    # ------------------------------------------------------------------
    # Tier 1 - Free Public JSON APIs
    # ------------------------------------------------------------------

    async def _search_remote_ok(self) -> list[Job]:
        """RemoteOK public JSON API."""
        jobs: list[Job] = []
        async with aiohttp.ClientSession() as s:
            for term in self._roles:
                role = term.get("role", "")
                tag = role.lower().replace(" ", "-")
                data = await _get_json(s, f"https://remoteok.com/api?tag={tag}")
                if not isinstance(data, list):
                    continue
                for item in data[1:21]:
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
                                url=item.get("url", ""),
                                source="remote-ok",
                                posted_date=item.get("date", ""),
                                salary=item.get("salary", ""),
                                search_term=role,
                            )
                        )
        return jobs

    async def _search_remotive(self) -> list[Job]:
        """Remotive public JSON API."""
        jobs: list[Job] = []
        category_map = {
            "python": "software-dev",
            "devops": "devops",
            "site reliability engineer": "devops",
            "javascript": "frontend",
            "ai": "data",
        }
        async with aiohttp.ClientSession() as s:
            for term in self._roles:
                role = term.get("role", "")
                cat = category_map.get(role.lower(), "software-dev")
                data = await _get_json(
                    s, f"https://remotive.com/api/remote-jobs?category={cat}&limit=20"
                )
                if not isinstance(data, dict):
                    continue
                for item in data.get("jobs", [])[:20]:
                    jobs.append(
                        Job(
                            title=item.get("title", ""),
                            company=item.get("company_name", ""),
                            location=item.get("candidate_required_location", "Remote"),
                            url=item.get("url", ""),
                            source="remotive",
                            posted_date=item.get("published_at", ""),
                            salary=item.get("salary", ""),
                            search_term=role,
                        )
                    )
        return jobs

    async def _search_arbeitnow(self) -> list[Job]:
        """Arbeitnow free public API - international remote jobs."""
        jobs: list[Job] = []
        async with aiohttp.ClientSession() as s:
            for term in self._roles:
                role = term.get("role", "")
                url = f"https://www.arbeitnow.com/api/job-board-api?search={role.replace(' ', '+')}&remote=true"
                data = await _get_json(s, url)
                if not isinstance(data, dict):
                    continue
                for item in data.get("data", [])[:20]:
                    jobs.append(
                        Job(
                            title=item.get("title", ""),
                            company=item.get("company_name", ""),
                            location=item.get("location", "Remote"),
                            url=item.get("url", ""),
                            source="arbeitnow",
                            posted_date=item.get("created_at", ""),
                            description=item.get("description", "")[:300]
                            if item.get("description")
                            else None,
                            search_term=role,
                        )
                    )
        return jobs

    async def _search_himalayas(self) -> list[Job]:
        """Himalayas.app free public API."""
        jobs: list[Job] = []
        async with aiohttp.ClientSession() as s:
            for term in self._roles:
                role = term.get("role", "")
                url = f"https://himalayas.app/jobs/api?q={role.replace(' ', '+')}&limit=20"
                data = await _get_json(s, url)
                if not isinstance(data, dict):
                    continue
                for item in data.get("jobs", [])[:20]:
                    jobs.append(
                        Job(
                            title=item.get("title", ""),
                            company=item.get("companyName", ""),
                            location=item.get("location", "Remote"),
                            url=item.get("applicationLink", item.get("url", "")),
                            source="himalayas",
                            posted_date=item.get("createdAt", ""),
                            salary=item.get("salary", ""),
                            search_term=role,
                        )
                    )
        return jobs

    async def _search_jobicy(self) -> list[Job]:
        """Jobicy free public API - remote jobs."""
        jobs: list[Job] = []
        async with aiohttp.ClientSession() as s:
            for term in self._roles:
                role = term.get("role", "")
                url = f"https://jobicy.com/api/v2/remote-jobs?count=20&tag={role.replace(' ', '+')}"
                data = await _get_json(s, url)
                if not isinstance(data, dict):
                    continue
                for item in data.get("jobs", [])[:20]:
                    jobs.append(
                        Job(
                            title=item.get("jobTitle", ""),
                            company=item.get("companyName", ""),
                            location=item.get("jobGeo", "Remote"),
                            url=item.get("url", ""),
                            source="jobicy",
                            posted_date=item.get("pubDate", ""),
                            salary=item.get("annualSalaryMin", ""),
                            search_term=role,
                        )
                    )
        return jobs

    async def _search_the_muse(self) -> list[Job]:
        """The Muse public API."""
        jobs: list[Job] = []
        settings = get_settings()
        async with aiohttp.ClientSession() as s:
            for term in self._roles:
                role = term.get("role", "")
                params: dict = {"category": role, "page": 1, "descending": "true"}
                if settings.the_muse_api_key:
                    params["api_key"] = settings.the_muse_api_key
                qs = "&".join(f"{k}={v}" for k, v in params.items())
                data = await _get_json(
                    s, f"https://www.themuse.com/api/public/jobs?{qs}"
                )
                if not isinstance(data, dict):
                    continue
                for item in data.get("results", [])[:20]:
                    company = item.get("company", {}).get("name", "")
                    locations = item.get("locations", [])
                    location = (
                        locations[0].get("name", "Remote") if locations else "Remote"
                    )
                    jobs.append(
                        Job(
                            title=item.get("name", ""),
                            company=company,
                            location=location,
                            url=item.get("refs", {}).get("landing_page", ""),
                            source="the-muse",
                            posted_date=item.get("publication_date", ""),
                            search_term=role,
                        )
                    )
        return jobs

    # ------------------------------------------------------------------
    # Tier 2 - RSS Feeds
    # ------------------------------------------------------------------

    async def _search_weworkremotely_rss(self) -> list[Job]:
        """We Work Remotely - parse public RSS feed."""
        jobs: list[Job] = []
        feed_urls = [
            "https://weworkremotely.com/remote-jobs.rss",
            "https://weworkremotely.com/categories/remote-programming-jobs.rss",
            "https://weworkremotely.com/categories/remote-devops-sysadmin-jobs.rss",
        ]
        keywords = {t.get("role", "").lower() for t in self._roles} | {
            kw.lower() for t in self._roles for kw in t.get("keywords", [])
        }

        async with aiohttp.ClientSession() as s:
            for feed_url in feed_urls:
                text = await _get_text(s, feed_url)
                if not text:
                    continue
                try:
                    root = ET.fromstring(text)
                    channel = root.find("channel")
                    if channel is None:
                        continue
                    for item in channel.findall("item")[:30]:
                        title_el = item.find("title")
                        link_el = item.find("link")
                        region_el = item.find("region")
                        company_el = item.find("company")
                        date_el = item.find("pubDate")

                        title = title_el.text or "" if title_el is not None else ""
                        link = link_el.text or "" if link_el is not None else ""
                        region = (
                            region_el.text or "Remote"
                            if region_el is not None
                            else "Remote"
                        )
                        company = (
                            company_el.text or "" if company_el is not None else ""
                        )
                        pub_date = date_el.text or "" if date_el is not None else ""

                        # Basic keyword relevance filter
                        title_lower = title.lower()
                        if keywords and not any(kw in title_lower for kw in keywords):
                            continue

                        if link:
                            jobs.append(
                                Job(
                                    title=title,
                                    company=company,
                                    location=region,
                                    url=link,
                                    source="we-work-remotely",
                                    posted_date=pub_date,
                                    search_term="rss",
                                )
                            )
                except ET.ParseError as exc:
                    logger.error(f"WWR RSS parse error: {exc}")

        return jobs

    # ------------------------------------------------------------------
    # Tier 3 - API-key boards
    # ------------------------------------------------------------------

    async def _search_adzuna(self, auth) -> list[Job]:
        """Adzuna Jobs API (requires ADZUNA_APP_ID + ADZUNA_API_KEY)."""
        jobs: list[Job] = []
        settings = get_settings()
        country = settings.adzuna_country or "us"
        base = f"https://api.adzuna.com/v1/api/jobs/{country}/search"

        async with aiohttp.ClientSession() as s:
            for term in self._roles:
                role = term.get("role", "")
                params = {
                    **auth.adzuna.auth_params(),
                    "what": role,
                    "results_per_page": 20,
                    "content-type": "application/json",
                }
                data = await _get_json(s, f"{base}/1", params=params)
                if not isinstance(data, dict):
                    continue
                for item in data.get("results", [])[:20]:
                    company = item.get("company", {}).get("display_name", "")
                    location = item.get("location", {}).get("display_name", "")
                    jobs.append(
                        Job(
                            title=item.get("title", ""),
                            company=company,
                            location=location,
                            url=item.get("redirect_url", ""),
                            source="adzuna",
                            posted_date=item.get("created", ""),
                            salary=str(item.get("salary_min", "")),
                            description=item.get("description", "")[:300],
                            search_term=role,
                        )
                    )
        return jobs

    async def _search_indeed(self, auth) -> list[Job]:
        """Indeed Publisher API (requires INDEED_PUBLISHER_ID)."""
        jobs: list[Job] = []
        base_params = auth.indeed.auth_params()

        async with aiohttp.ClientSession() as s:
            for term in self._roles:
                role = term.get("role", "")
                params = {
                    **base_params,
                    "q": role,
                    "l": "",
                    "sort": "date",
                    "radius": 25,
                    "st": "",
                    "jt": "fulltime",
                    "start": 0,
                    "limit": 20,
                    "latlong": 1,
                    "co": "us",
                    "chnl": "",
                    "userip": "1.2.3.4",
                    "useragent": "Mozilla/5.0",
                }
                data = await _get_json(
                    s, "http://api.indeed.com/ads/apisearch", params=params
                )
                if not isinstance(data, dict):
                    continue
                for item in data.get("results", [])[:20]:
                    jobs.append(
                        Job(
                            title=item.get("jobtitle", ""),
                            company=item.get("company", ""),
                            location=f"{item.get('city','')}, {item.get('state','')}".strip(
                                ", "
                            ),
                            url=item.get("url", ""),
                            source="indeed",
                            posted_date=item.get("date", ""),
                            search_term=role,
                        )
                    )
        return jobs

    async def _search_ziprecruiter(self, auth) -> list[Job]:
        """ZipRecruiter Partner API (requires ZIPRECRUITER_API_KEY)."""
        jobs: list[Job] = []
        headers = {**_HEADERS, **auth.ziprecruiter.auth_headers()}

        async with aiohttp.ClientSession() as s:
            for term in self._roles:
                role = term.get("role", "")
                params = {"search": role, "jobs_per_page": 20}
                data = await _get_json(
                    s,
                    "https://api.ziprecruiter.com/jobs/v1",
                    params=params,
                    headers=headers,
                )
                if not isinstance(data, dict):
                    continue
                for item in data.get("jobs", [])[:20]:
                    jobs.append(
                        Job(
                            title=item.get("name", ""),
                            company=item.get("hiring_company", {}).get("name", ""),
                            location=item.get("location", ""),
                            url=item.get("job_url", ""),
                            source="ziprecruiter",
                            posted_date=item.get("posted_time", ""),
                            salary=item.get("salary_interval", ""),
                            search_term=role,
                        )
                    )
        return jobs

    # ------------------------------------------------------------------
    # Tier 4 - OAuth (LinkedIn)
    # ------------------------------------------------------------------

    async def _search_linkedin(self, auth) -> list[Job]:
        """LinkedIn Jobs API (requires OAuth client credentials)."""
        jobs: list[Job] = []
        token = await auth.linkedin.get_token()
        if not token:
            logger.debug("LinkedIn: no valid token - skipping.")
            return jobs

        headers = {**_HEADERS, **token.auth_header}
        async with aiohttp.ClientSession() as s:
            for term in self._roles:
                role = term.get("role", "")
                params = {"keywords": role, "count": 20, "start": 0}
                data = await _get_json(
                    s,
                    "https://api.linkedin.com/v2/jobSearch",
                    params=params,
                    headers=headers,
                )
                if not isinstance(data, dict):
                    continue
                for item in data.get("elements", [])[:20]:
                    job_data = item.get("jobPosting", {})
                    title = job_data.get("title", "")
                    company = (
                        job_data.get("company", {}).get("name", "")
                        if isinstance(job_data.get("company"), dict)
                        else ""
                    )
                    location_data = job_data.get("formattedLocation", "")
                    job_id = job_data.get("id", "")
                    url = (
                        f"https://www.linkedin.com/jobs/view/{job_id}/"
                        if job_id
                        else ""
                    )
                    jobs.append(
                        Job(
                            title=title,
                            company=company,
                            location=location_data,
                            url=url,
                            source="linkedin",
                            posted_date=str(job_data.get("listedAt", "")),
                            search_term=role,
                        )
                    )
        return jobs

    # ------------------------------------------------------------------
    # Tier 5 - ATS Aggregators
    # ------------------------------------------------------------------

    async def _search_lever(self, settings) -> list[Job]:
        """Lever ATS public postings API."""
        jobs: list[Job] = []
        companies = [
            c.strip() for c in settings.lever_companies.split(",") if c.strip()
        ]
        keywords = {t.get("role", "").lower() for t in self._roles}

        async with aiohttp.ClientSession() as s:
            for company in companies:
                url = f"https://api.lever.co/v0/postings/{company}?mode=json"
                data = await _get_json(s, url)
                if not isinstance(data, list):
                    continue
                for item in data[:15]:
                    title = item.get("text", "")
                    # Filter to relevant roles only
                    if keywords and not any(kw in title.lower() for kw in keywords):
                        continue
                    jobs.append(
                        Job(
                            title=title,
                            company=company.title(),
                            location=item.get("categories", {}).get("location", ""),
                            url=item.get("hostedUrl", item.get("applyUrl", "")),
                            source="lever",
                            posted_date=str(item.get("createdAt", "")),
                            description=item.get("description", "")[:300],
                            search_term=f"lever/{company}",
                        )
                    )
        return jobs

    async def _search_ashby(self, settings) -> list[Job]:
        """Ashby ATS public postings API."""
        jobs: list[Job] = []
        companies = [
            c.strip() for c in settings.ashby_companies.split(",") if c.strip()
        ]
        keywords = {t.get("role", "").lower() for t in self._roles}

        async with aiohttp.ClientSession() as s:
            for company in companies:
                url = f"https://api.ashbyhq.com/posting-api/job-board/{company}"
                data = await _get_json(s, url)
                if not isinstance(data, dict):
                    continue
                for item in data.get("jobPostings", [])[:15]:
                    title = item.get("title", "")
                    if keywords and not any(kw in title.lower() for kw in keywords):
                        continue
                    location = ""
                    loc = item.get("location")
                    if isinstance(loc, dict):
                        location = loc.get("locationStr", "")
                    elif isinstance(loc, str):
                        location = loc
                    jobs.append(
                        Job(
                            title=title,
                            company=company.title(),
                            location=location,
                            url=item.get("jobUrl", item.get("applyUrl", "")),
                            source="ashby",
                            posted_date=item.get("publishedAt", ""),
                            search_term=f"ashby/{company}",
                        )
                    )
        return jobs

    async def _search_greenhouse(self, settings) -> list[Job]:
        """Greenhouse ATS public job board API."""
        jobs: list[Job] = []
        companies = [
            c.strip() for c in settings.greenhouse_companies.split(",") if c.strip()
        ]
        keywords = {t.get("role", "").lower() for t in self._roles}

        async with aiohttp.ClientSession() as s:
            for company in companies:
                url = f"https://boards-api.greenhouse.io/v1/boards/{company}/jobs?content=true"
                data = await _get_json(s, url)
                if not isinstance(data, dict):
                    continue
                for item in data.get("jobs", [])[:15]:
                    title = item.get("title", "")
                    if keywords and not any(kw in title.lower() for kw in keywords):
                        continue
                    location = (
                        item.get("location", {}).get("name", "")
                        if isinstance(item.get("location"), dict)
                        else ""
                    )
                    jobs.append(
                        Job(
                            title=title,
                            company=company.title(),
                            location=location,
                            url=item.get("absolute_url", ""),
                            source="greenhouse",
                            posted_date=item.get("updated_at", ""),
                            search_term=f"greenhouse/{company}",
                        )
                    )
        return jobs

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    def filter_new_jobs(self, existing_jobs: list[Job]) -> list[Job]:
        """Filter out jobs already tracked."""
        existing_urls = {job.url for job in existing_jobs}
        return [job for job in self.jobs if job.url not in existing_urls]


# ---------------------------------------------------------------------------
# Quick test
# ---------------------------------------------------------------------------

if __name__ == "__main__":

    async def test():
        searcher = JobSearcher()
        jobs = await searcher.search_all()
        print(f"Found {len(jobs)} jobs")
        from collections import Counter

        counts = Counter(j.source for j in jobs)
        for source, count in sorted(counts.items()):
            print(f"  {source:25s} {count:3d} jobs")

    asyncio.run(test())
