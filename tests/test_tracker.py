import json

from modules.tracker import ApplicationTracker


def test_tracker_load_empty(tmp_data_dir):
    tracker = ApplicationTracker(data_path=str(tmp_data_dir / "apps.json"))
    assert len(tracker.get_applications()) == 0


def test_tracker_add_application(tmp_data_dir, sample_job):
    data_file = tmp_data_dir / "apps.json"
    tracker = ApplicationTracker(data_path=str(data_file))

    success = tracker.add_application(sample_job)
    assert success is True
    assert len(tracker.get_applications()) == 1

    # Verify file was written
    with open(data_file) as f:
        data = json.load(f)
        assert len(data) == 1
        assert data[0]["url"] == sample_job.url


def test_tracker_add_duplicate(tmp_data_dir, sample_job):
    tracker = ApplicationTracker(data_path=str(tmp_data_dir / "apps.json"))
    tracker.add_application(sample_job)

    success = tracker.add_application(sample_job)
    assert success is False
    assert len(tracker.get_applications()) == 1


def test_tracker_update_status(tmp_data_dir, sample_job):
    tracker = ApplicationTracker(data_path=str(tmp_data_dir / "apps.json"))
    tracker.add_application(sample_job)

    success = tracker.update_status(sample_job.url, "interview", "Great news!")
    assert success is True

    app = tracker.get_applications()[0]
    assert app.status == "interview"
    assert app.notes == "Great news!"


def test_tracker_get_summary(tmp_data_dir, sample_job):
    tracker = ApplicationTracker(data_path=str(tmp_data_dir / "apps.json"))
    tracker.add_application(sample_job)

    summary = tracker.get_summary()
    assert summary["total"] == 1
    assert summary["applied"] == 1
