import pytest
from aioresponses import aioresponses
from modules.job_search import JobSearcher

@pytest.mark.asyncio
async def test_search_remote_ok(tmp_config_file):
    searcher = JobSearcher(config_path=str(tmp_config_file))
    
    with aioresponses() as m:
        # Mocking Remote OK API
        # The first item in the response is usually a disclaimer
        mock_response = [
            {"legal": "notice"},
            {
                "position": "Python Developer",
                "company": "Test Co",
                "location": "Remote",
                "url": "https://remoteok.com/job1",
                "date": "2023-01-01"
            }
        ]
        m.get("https://remoteok.com/api?tag=python", payload=mock_response)
        
        jobs = await searcher._search_remote_ok()
        
        assert len(jobs) == 1
        assert jobs[0].title == "Python Developer"
        assert jobs[0].company == "Test Co"
        assert jobs[0].source == "remote-ok"

@pytest.mark.asyncio
async def test_search_all(tmp_config_file):
    searcher = JobSearcher(config_path=str(tmp_config_file))
    
    with aioresponses() as m:
        # Remote OK
        m.get("https://remoteok.com/api?tag=python", payload=[{"legal": "notice"}, {"position": "Dev", "company": "Co", "url": "url"}])
        # Indeed (currently returns empty list)
        
        jobs = await searcher.search_all()
        assert len(jobs) == 1

def test_filter_new_jobs(tmp_config_file, sample_job):
    searcher = JobSearcher(config_path=str(tmp_config_file))
    searcher.jobs = [sample_job]
    
    # URL already exists
    existing_jobs = [sample_job]
    new_jobs = searcher.filter_new_jobs(existing_jobs)
    assert len(new_jobs) == 0
    
    # URL is new
    new_jobs = searcher.filter_new_jobs([])
    assert len(new_jobs) == 1
