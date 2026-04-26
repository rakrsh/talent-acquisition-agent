"""Job Agent - 12-Factor App compliant talent acquisition agent."""

import asyncio
import json
from dataclasses import asdict

from config import logger
from modules.job_search import JobSearcher
from modules.notifications import NotificationService
from modules.tracker import ApplicationTracker
from settings import get_settings


async def run_job_search():
    """Main job search and notification pipeline."""
    settings = get_settings()

    logger.info(f"Job Agent v1.1.0 starting | Mode: {settings.env_mode}")

    # Initialize services
    searcher = JobSearcher()
    notifier = NotificationService()
    tracker = ApplicationTracker()

    # Show current stats
    summary = tracker.get_summary()
    logger.info(
        f"Current applications: {summary['total']} total | "
        f"Applied: {summary['applied']} | Pending: {summary['pending']}"
    )

    # Search for jobs
    logger.info("Searching for jobs...")
    jobs = await searcher.search_all()
    logger.info(f"Found {len(jobs)} jobs")

    if not jobs:
        logger.warning("No jobs found. Check input/search_criteria.json")
        return

    # Filter new jobs (not already in tracker)
    existing_urls = {app.url for app in tracker.get_applications()}
    new_jobs = [job for job in jobs if job.url not in existing_urls]
    logger.info(f"New jobs (not yet applied): {len(new_jobs)}")

    if new_jobs:
        # Notify about new jobs
        logger.info("Sending notifications...")
        notifier.notify_new_jobs(new_jobs)

        # Save discovered jobs to file
        jobs_file = tracker.data_path.parent / "discovered_jobs.json"
        with open(jobs_file, "w") as f:
            json.dump([asdict(job) for job in new_jobs], f, indent=2)
        logger.info(f"Discovered jobs saved to: {jobs_file}")

        if settings.auto_apply_enabled:
            logger.info("Auto-apply enabled - would apply to jobs here")
        else:
            logger.info("Auto-apply disabled. Set AUTO_APPLY_ENABLED=true to enable.")

    # Final summary
    final_summary = tracker.get_summary()
    if final_summary["total"] > 0:
        logger.info(
            f"Job search complete! Total tracked: {final_summary['total']} | "
            f"Data saved to: {tracker.data_path}"
        )
    else:
        logger.info(
            f"Job search complete! Found {len(jobs)} jobs | "
            f"Discovered jobs saved to: {tracker.data_path.parent / 'discovered_jobs.json'}"
        )


async def main():
    """Entry point."""
    await run_job_search()


if __name__ == "__main__":
    asyncio.run(main())
