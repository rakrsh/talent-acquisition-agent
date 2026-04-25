"""Application tracker - records all job applications locally."""

import json
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

from settings import get_settings


@dataclass
class JobApplication:
    """Record of a job application."""

    title: str
    company: str
    location: str
    url: str
    source: str
    applied_date: str
    status: str = "applied"  # applied, pending, rejected, interview
    notes: str = ""


class ApplicationTracker:
    """Tracks all job applications in a local JSON file."""

    def __init__(self, data_path: Optional[str] = None):
        settings = get_settings()

        if data_path:
            self.data_path = Path(data_path)
        else:
            # Use configurable data directory
            data_dir = Path(settings.data_dir)
            data_dir.mkdir(parents=True, exist_ok=True)
            self.data_path = data_dir / "applications.json"

        self.data_path.parent.mkdir(parents=True, exist_ok=True)
        self.applications: list[JobApplication] = self._load()

    def _load(self) -> list[JobApplication]:
        """Load applications from JSON file."""
        if self.data_path.exists():
            with open(self.data_path) as f:
                data = json.load(f)
                return [JobApplication(**app) for app in data]
        return []

    def _save(self) -> None:
        """Save applications to JSON file."""
        with open(self.data_path, "w") as f:
            json.dump([asdict(app) for app in self.applications], f, indent=2)

    def add_application(self, job) -> bool:
        """Record a new job application."""
        # Check if already applied
        if any(app.url == job.url for app in self.applications):
            print(f"Already applied: {job.title} @ {job.company}")
            return False

        application = JobApplication(
            title=job.title,
            company=job.company,
            location=job.location,
            url=job.url,
            source=job.source,
            applied_date=datetime.now().isoformat(),
            status="applied",
        )

        self.applications.append(application)
        self._save()
        print(f"Recorded: {job.title} @ {job.company}")
        return True

    def get_applications(self, status: Optional[str] = None) -> list[JobApplication]:
        """Get all applications, optionally filtered by status."""
        if status:
            return [app for app in self.applications if app.status == status]
        return self.applications

    def update_status(self, url: str, status: str, notes: str = "") -> bool:
        """Update application status."""
        for app in self.applications:
            if app.url == url:
                app.status = status
                app.notes = notes
                self._save()
                return True
        return False

    def get_summary(self) -> dict:
        """Get application statistics."""
        return {
            "total": len(self.applications),
            "applied": len([a for a in self.applications if a.status == "applied"]),
            "pending": len([a for a in self.applications if a.status == "pending"]),
            "interview": len([a for a in self.applications if a.status == "interview"]),
            "rejected": len([a for a in self.applications if a.status == "rejected"]),
        }

    def export_csv(self, output_path: Optional[str] = None) -> str:
        """Export applications to CSV."""
        if output_path is None:
            output_path = str(self.data_path.with_suffix(".csv"))

        import csv

        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=[
                    "title",
                    "company",
                    "location",
                    "url",
                    "source",
                    "applied_date",
                    "status",
                    "notes",
                ],
            )
            writer.writeheader()
            for app in self.applications:
                writer.writerow(asdict(app))

        return str(output_path)


if __name__ == "__main__":
    tracker = ApplicationTracker()
    print(f"Tracker initialized at: {tracker.data_path}")
    print(f"Summary: {tracker.get_summary()}")
