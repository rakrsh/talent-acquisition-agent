from unittest.mock import patch

from app import app
from fastapi.testclient import TestClient
from modules.job_search import Job

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["service"] == "search-service"


@patch("modules.job_search.JobSearcher.search_all")
def test_search_endpoint(mock_search):
    mock_search.return_value = [
        Job(title="Dev", company="Co", location="Loc", url="http://url", source="src")
    ]
    response = client.get("/search")
    assert response.status_code == 200
    assert response.json()["count"] == 1
    assert response.json()["jobs"][0]["title"] == "Dev"
