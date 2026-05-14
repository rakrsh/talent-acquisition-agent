import json
import logging
import os

from config import JSONFormatter, setup_logging


def test_json_formatter():
    formatter = JSONFormatter()
    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname="test.py",
        lineno=10,
        msg="Test message",
        args=(),
        exc_info=None,
    )
    formatted = formatter.format(record)
    data = json.loads(formatted)

    assert data["message"] == "Test message"
    assert data["level"] == "INFO"
    assert "timestamp" in data


def test_setup_logging_dev():
    os.environ["ENV_MODE"] = "development"
    logger = setup_logging()
    assert logger.level == logging.INFO
    assert len(logger.handlers) == 1
    # Check formatter type if possible, or just that it didn't crash


def test_setup_logging_prod():
    os.environ["ENV_MODE"] = "production"
    logger = setup_logging()
    assert isinstance(logger.handlers[0].formatter, JSONFormatter)
    del os.environ["ENV_MODE"]
