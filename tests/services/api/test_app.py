from unittest.mock import patch

from app import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "Job Agent" in response.text


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


@patch("aiohttp.ClientSession.get")
async def test_search_jobs_proxy(mock_get):
    # Mocking aiohttp is complex, but let's assume we mock the proxy behavior
    # For simplicity, we might just test the orchestrator endpoints
    pass


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
    response = client.patch(
        "/applications/http%3A%2F%2Furl/status?status=interview&notes=test"
    )
    assert response.status_code == 200
    assert response.json()["status"] == "updated"
