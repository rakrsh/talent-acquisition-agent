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
    # -- Auth Credentials (Factor III - all from env, never hardcoded) --
    # ===================================================================

    # LinkedIn OAuth 2.0
    linkedin_client_id: str = Field(default="", validation_alias="LINKEDIN_CLIENT_ID")
    linkedin_client_secret: str = Field(
        default="", validation_alias="LINKEDIN_CLIENT_SECRET"
    )

    # Adzuna API (developer.adzuna.com - free tier available)
    adzuna_app_id: str = Field(default="", validation_alias="ADZUNA_APP_ID")
    adzuna_api_key: str = Field(default="", validation_alias="ADZUNA_API_KEY")
    adzuna_country: str = Field(
        default="us", validation_alias="ADZUNA_COUNTRY"
    )  # us, gb, au, ca, de, fr, in, nl, nz, pl, ru, sg, za

    # Indeed Publisher API (apply at indeed.com/publisher)
    indeed_publisher_id: str = Field(default="", validation_alias="INDEED_PUBLISHER_ID")

    # ZipRecruiter Partner API
    ziprecruiter_api_key: str = Field(
        default="", validation_alias="ZIPRECRUITER_API_KEY"
    )

    # GitHub personal access token (optional - avoids 60 req/h limit)
    github_token: str = Field(default="", validation_alias="GITHUB_TOKEN")

    # The Muse (no auth required, but optional api_key lifts rate limit)
    the_muse_api_key: str = Field(default="", validation_alias="THE_MUSE_API_KEY")

    # ===================================================================
    # Job Search - enabled sources
    # ===================================================================

    # Always-on free public API boards
    remote_ok_enabled: bool = Field(default=True, validation_alias="REMOTE_OK_ENABLED")
    remotive_enabled: bool = Field(default=True, validation_alias="REMOTIVE_ENABLED")
    arbeitnow_enabled: bool = Field(
        default=True, validation_alias="ARBEITNOW_ENABLED"
    )  # free, no auth
    himalayas_enabled: bool = Field(
        default=True, validation_alias="HIMALAYAS_ENABLED"
    )  # free, no auth
    jobicy_enabled: bool = Field(
        default=True, validation_alias="JOBICY_ENABLED"
    )  # free, no auth
    the_muse_enabled: bool = Field(
        default=True, validation_alias="THE_MUSE_ENABLED"
    )  # free, no auth

    # RSS-feed boards
    we_work_remotely_enabled: bool = Field(
        default=True, validation_alias="WE_WORK_REMOTELY_ENABLED"
    )

    # API-key required boards
    adzuna_enabled: bool = Field(default=False, validation_alias="ADZUNA_ENABLED")
    indeed_enabled: bool = Field(default=False, validation_alias="INDEED_ENABLED")
    ziprecruiter_enabled: bool = Field(
        default=False, validation_alias="ZIPRECRUITER_ENABLED"
    )

    # OAuth 2.0 boards
    linkedin_enabled: bool = Field(default=False, validation_alias="LINKEDIN_ENABLED")

    # ATS aggregators (public APIs - company-specific postings)
    lever_enabled: bool = Field(default=True, validation_alias="LEVER_ENABLED")
    ashby_enabled: bool = Field(default=True, validation_alias="ASHBY_ENABLED")
    greenhouse_enabled: bool = Field(
        default=True, validation_alias="GREENHOUSE_ENABLED"
    )

    # Deprecated / stub only (kept for backward compat)
    glassdoor_enabled: bool = Field(default=False, validation_alias="GLASSDOOR_ENABLED")
    monster_enabled: bool = Field(default=False, validation_alias="MONSTER_ENABLED")
    careerjet_enabled: bool = Field(default=False, validation_alias="CAREERJET_ENABLED")
    jooble_enabled: bool = Field(default=False, validation_alias="JOOBLE_ENABLED")
    simplyhired_enabled: bool = Field(
        default=False, validation_alias="SIMPLYHIRED_ENABLED"
    )

    # ===================================================================
    # Search behaviour
    # ===================================================================
    max_jobs_per_search: int = Field(default=20, validation_alias="MAX_JOBS_PER_SEARCH")
    search_interval_hours: int = Field(
        default=24, validation_alias="SEARCH_INTERVAL_HOURS"
    )
    auto_apply_enabled: bool = Field(
        default=False, validation_alias="AUTO_APPLY_ENABLED"
    )

    # ATS company lists (comma-separated slugs)
    lever_companies: str = Field(
        default="stripe,airbnb,notion,figma,twilio,datadog,snowflake,cloudflare,elastic,gitlab",
        validation_alias="LEVER_COMPANIES",
    )
    ashby_companies: str = Field(
        default="linear,cal.com,resend,raycast,polymarket,loom,retool,dbt-labs",
        validation_alias="ASHBY_COMPANIES",
    )
    greenhouse_companies: str = Field(
        default="shopify,discord,reddit,intercom,dropbox,squarespace,duolingo,eventbrite,hubspot,zendesk",
        validation_alias="GREENHOUSE_COMPANIES",
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
