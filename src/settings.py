"""Application settings - 12-Factor App Factor III: Configuration."""

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Centralized configuration - all config in environment variables."""

    # ===================================================================
    # Factor I: Codebase & Factor III: Config
    # ===================================================================
    env_mode: str = Field(default="development", validation_alias="ENV_MODE")
    log_level: str = Field(default="INFO", validation_alias="LOG_LEVEL")

    # ===================================================================
    # LLM Configuration (for AI-powered features)
    # ===================================================================
    ollama_host: str = Field(
        default="http://localhost:11434", validation_alias="OLLAMA_HOST"
    )
    llm_model: str = Field(default="llama3", validation_alias="LLM_MODEL")

    # ===================================================================
    # Factor IV: Backing Services
    # ===================================================================
    database_url: str = Field(
        default="sqlite:///./job_agent.db", validation_alias="DATABASE_URL"
    )
    db_type: str = Field(default="sqlite", validation_alias="DB_TYPE")

    # ===================================================================
    # Notification Services
    # ===================================================================
    sender_email: str = Field(default="", validation_alias="SENDER_EMAIL")
    sender_password: str = Field(default="", validation_alias="SENDER_PASSWORD")
    recipient_email: str = Field(default="", validation_alias="RECIPIENT_EMAIL")

    smtp_host: str = Field(default="smtp.gmail.com", validation_alias="SMTP_HOST")
    smtp_port: int = Field(default=587, validation_alias="SMTP_PORT")

    # Twilio SMS
    twilio_sid: str = Field(default="", validation_alias="TWILIO_SID")
    twilio_token: str = Field(default="", validation_alias="TWILIO_TOKEN")
    twilio_phone: str = Field(default="", validation_alias="TWILIO_PHONE")
    recipient_phone: str = Field(default="", validation_alias="RECIPIENT_PHONE")

    # ===================================================================
    # Job Search Configuration
    # ===================================================================
    remote_ok_enabled: bool = Field(default=True, validation_alias="REMOTE_OK_ENABLED")
    remotive_enabled: bool = Field(default=True, validation_alias="REMOTIVE_ENABLED")
    linkedin_enabled: bool = Field(default=False, validation_alias="LINKEDIN_ENABLED")
    indeed_enabled: bool = Field(default=False, validation_alias="INDEED_ENABLED")

    # Global Job Boards (Factor IV: Backing Services)
    we_work_remotely_enabled: bool = Field(
        default=False, validation_alias="WE_WORK_REMOTELY_ENABLED"
    )
    linkedin_job_enabled: bool = Field(
        default=False, validation_alias="LINKEDIN_JOB_ENABLED"
    )
    indeed_job_enabled: bool = Field(
        default=False, validation_alias="INDEED_JOB_ENABLED"
    )
    glassdoor_enabled: bool = Field(default=False, validation_alias="GLASSDOOR_ENABLED")
    monster_enabled: bool = Field(default=False, validation_alias="MONSTER_ENABLED")
    careerjet_enabled: bool = Field(default=False, validation_alias="CAREERJET_ENABLED")
    jooble_enabled: bool = Field(default=False, validation_alias="JOOBLE_ENABLED")
    simplyhired_enabled: bool = Field(
        default=False, validation_alias="SIMPLYHIRED_ENABLED"
    )
    ziprecruiter_enabled: bool = Field(
        default=False, validation_alias="ZIPRECRUITER_ENABLED"
    )
    lever_enabled: bool = Field(default=False, validation_alias="LEVER_ENABLED")
    greenhouse_enabled: bool = Field(
        default=False, validation_alias="GREENHOUSE_ENABLED"
    )
    ashby_enabled: bool = Field(default=False, validation_alias="ASHBY_ENABLED")

    max_jobs_per_search: int = Field(default=20, validation_alias="MAX_JOBS_PER_SEARCH")
    search_interval_hours: int = Field(
        default=24, validation_alias="SEARCH_INTERVAL_HOURS"
    )
    auto_apply_enabled: bool = Field(
        default=False, validation_alias="AUTO_APPLY_ENABLED"
    )

    # ===================================================================
    # Factor VII: Port Binding (HTTP server)
    # ===================================================================
    http_host: str = Field(default="0.0.0.0", validation_alias="HTTP_HOST")
    http_port: int = Field(default=8080, validation_alias="HTTP_PORT")

    # ===================================================================
    # Factor VI: Process Configuration
    # ===================================================================
    config_file_path: str = Field(
        default="input/search_criteria.json", validation_alias="CONFIG_FILE_PATH"
    )
    data_dir: str = Field(default="data", validation_alias="DATA_DIR")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # Allow extra fields in .env


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get settings instance - enables testing with overrides."""
    return settings
