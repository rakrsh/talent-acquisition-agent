import json

import pytest
from modules.job_search import Job
from modules.tracker import JobApplication


@pytest.fixture
def sample_job():
    return Job(
        title="Software Engineer",
        company="Tech Corp",
        location="Remote",
        url="https://example.com/job1",
        source="remote-ok",
        posted_date="2023-01-01",
    )


@pytest.fixture
def sample_application():
    return JobApplication(
        title="Software Engineer",
        company="Tech Corp",
        location="Remote",
        url="https://example.com/job1",
        source="remote-ok",
        applied_date="2023-01-01T00:00:00",
        status="applied",
        notes="Test notes",
    )


@pytest.fixture
def tmp_data_dir(tmp_path):
    d = tmp_path / "data"
    d.mkdir()
    return d


@pytest.fixture
def tmp_config_file(tmp_path):
    f = tmp_path / "search_criteria.json"
    config = {
        "search_terms": [
            {
                "role": "python",
                "keywords": ["backend"],
                "locations": ["remote"],
                "job_types": ["full-time"],
            }
        ]
    }
    f.write_text(json.dumps(config))
    return f
