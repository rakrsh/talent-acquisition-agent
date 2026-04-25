import os
import pytest
from settings import Settings, get_settings

def test_settings_default():
    settings = Settings()
    assert settings.env_mode == "development"
    assert settings.log_level == "INFO"
    assert settings.http_port == 8080

def test_settings_env_override():
    os.environ["ENV_MODE"] = "production"
    os.environ["HTTP_PORT"] = "9090"
    settings = Settings()
    assert settings.env_mode == "production"
    assert settings.http_port == 9090
    # Cleanup
    del os.environ["ENV_MODE"]
    del os.environ["HTTP_PORT"]

def test_get_settings():
    settings = get_settings()
    assert isinstance(settings, Settings)
