import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from main import run_job_search
from modules.job_search import Job
from modules.tracker import JobApplication

@pytest.mark.asyncio
@patch("main.JobSearcher")
@patch("main.NotificationService")
@patch("main.ApplicationTracker")
@patch("main.get_settings")
async def test_run_job_search_success(mock_settings, mock_tracker_cls, mock_notif_cls, mock_search_cls):
    # Setup mocks
    mock_settings.return_value.env_mode = "test"
    mock_settings.return_value.auto_apply_enabled = False
    
    mock_tracker = mock_tracker_cls.return_value
    mock_tracker.get_summary.return_value = {"total": 0, "applied": 0, "pending": 0}
    mock_tracker.get_applications.return_value = []
    
    mock_search = mock_search_cls.return_value
    mock_search.search_all = AsyncMock(return_value=[
        Job(title="Dev", company="Co", location="Loc", url="http://url", source="src")
    ])
    
    mock_notif = mock_notif_cls.return_value
    
    # Run
    await run_job_search()
    
    # Verify
    assert mock_search.search_all.called
    assert mock_notif.notify_new_jobs.called
    assert mock_tracker.get_summary.call_count == 2

@pytest.mark.asyncio
@patch("main.JobSearcher")
@patch("main.NotificationService")
@patch("main.ApplicationTracker")
@patch("main.get_settings")
async def test_run_job_search_no_jobs(mock_settings, mock_tracker_cls, mock_notif_cls, mock_search_cls):
    mock_search = mock_search_cls.return_value
    mock_search.search_all = AsyncMock(return_value=[])
    
    await run_job_search()
    
    assert mock_search.search_all.called
    assert not mock_notif_cls.return_value.notify_new_jobs.called
