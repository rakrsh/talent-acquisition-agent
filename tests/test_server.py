from unittest.mock import patch

from fastapi.testclient import TestClient
from modules.job_search import Job
from server import app

client = TestClient(app)


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["service"] == "job-agent"


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


@patch("modules.job_search.JobSearcher.search_all")
def test_search_jobs(mock_search):
    mock_search.return_value = [
        Job(title="Dev", company="Co", location="Loc", url="http://url", source="src")
    ]
    response = client.get("/jobs")
    assert response.status_code == 200
    assert response.json()["count"] == 1
    assert response.json()["jobs"][0]["title"] == "Dev"


@patch("modules.tracker.ApplicationTracker.get_applications")
@patch("modules.tracker.ApplicationTracker.get_summary")
def test_get_applications(mock_summary, mock_apps):
    mock_apps.return_value = []
    mock_summary.return_value = {"total": 0}
    response = client.get("/applications")
    assert response.status_code == 200
    assert response.json()["count"] == 0


@patch("modules.tracker.ApplicationTracker.add_application")
def test_add_application(mock_add):
    mock_add.return_value = True
    payload = {
        "title": "Dev",
        "company": "Co",
        "location": "Loc",
        "url": "http://url",
        "source": "src",
    }
    response = client.post("/applications", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "recorded"


@patch("modules.tracker.ApplicationTracker.update_status")
def test_update_application_status(mock_update):
    mock_update.return_value = True
    response = client.patch("/applications/some-url/status?status=interview&notes=test")
    assert response.status_code == 200
    assert response.json()["status"] == "updated"
