"""Authentication module - manages credentials for job board APIs.

Supports three auth patterns:
  - API Key / Token (Adzuna, Indeed, ZipRecruiter, GitHub Jobs)
  - OAuth 2.0 Authorization Code flow (LinkedIn)
  - Session / Cookie (sites that need browser-based login)

All secrets are sourced exclusively from environment variables (12-Factor III).
No credentials are ever written to disk.
"""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field

import aiohttp
from config import logger
from settings import get_settings

# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


@dataclass
class TokenCredential:
    """Holds a bearer / access token with optional expiry."""

    access_token: str
    token_type: str = "Bearer"
    expires_at: float | None = None  # Unix timestamp
    refresh_token: str | None = None
    scope: str | None = None

    @property
    def is_expired(self) -> bool:
        """Return True if the token has expired (with a 60 s safety buffer)."""
        if self.expires_at is None:
            return False
        return time.time() >= (self.expires_at - 60)

    @property
    def auth_header(self) -> dict[str, str]:
        return {"Authorization": f"{self.token_type} {self.access_token}"}


@dataclass
class ApiKeyCredential:
    """Simple API-key / secret pair."""

    app_id: str
    api_key: str
    extra: dict = field(default_factory=dict)  # board-specific extras


# ---------------------------------------------------------------------------
# Individual authenticators
# ---------------------------------------------------------------------------


class LinkedInAuthenticator:
    """OAuth 2.0 client-credentials / PKCE flow for LinkedIn Jobs API.

    LinkedIn requires:
      LINKEDIN_CLIENT_ID  - OAuth app client id
      LINKEDIN_CLIENT_SECRET - OAuth app client secret

    The 3-legged OAuth flow (authorisation code) requires a browser
    redirect URI and is only suitable for a web app; here we use the
    *client credentials* grant which gives access to the Jobs Posting API
    for the authenticated organisation.

    Docs: https://docs.microsoft.com/en-us/linkedin/shared/authentication/
    """

    TOKEN_URL = "https://www.linkedin.com/oauth/v2/accessToken"
    SEARCH_URL = "https://api.linkedin.com/v2/jobSearch"

    def __init__(self) -> None:
        settings = get_settings()
        self.client_id = settings.linkedin_client_id
        self.client_secret = settings.linkedin_client_secret
        self._credential: TokenCredential | None = None

    @property
    def is_configured(self) -> bool:
        return bool(self.client_id and self.client_secret)

    async def get_token(self) -> TokenCredential | None:
        """Return a valid access token, refreshing if necessary."""
        if not self.is_configured:
            logger.debug("LinkedIn credentials not configured - skipping auth.")
            return None

        if self._credential and not self._credential.is_expired:
            return self._credential

        try:
            async with aiohttp.ClientSession() as session:
                resp = await session.post(
                    self.TOKEN_URL,
                    data={
                        "grant_type": "client_credentials",
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                    },
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                    timeout=aiohttp.ClientTimeout(total=15),
                )
                if resp.status == 200:
                    data = await resp.json()
                    self._credential = TokenCredential(
                        access_token=data["access_token"],
                        token_type=data.get("token_type", "Bearer"),
                        expires_at=time.time() + data.get("expires_in", 3600),
                        scope=data.get("scope"),
                    )
                    logger.info("LinkedIn: access token obtained.")
                    return self._credential
                else:
                    text = await resp.text()
                    logger.warning(
                        f"LinkedIn token request failed [{resp.status}]: {text[:200]}"
                    )
        except Exception as exc:
            logger.error(f"LinkedIn auth error: {exc}")

        return None


class AdzunaAuthenticator:
    """API-key authenticator for Adzuna.

    Requires:
      ADZUNA_APP_ID  — application id from developer.adzuna.com
      ADZUNA_API_KEY — application key

    Adzuna passes credentials as query parameters, not in headers.
    Docs: https://developer.adzuna.com/
    """

    def __init__(self) -> None:
        settings = get_settings()
        self.app_id = settings.adzuna_app_id
        self.api_key = settings.adzuna_api_key

    @property
    def is_configured(self) -> bool:
        return bool(self.app_id and self.api_key)

    def get_credential(self) -> ApiKeyCredential | None:
        if not self.is_configured:
            logger.debug("Adzuna credentials not configured.")
            return None
        return ApiKeyCredential(app_id=self.app_id, api_key=self.api_key)

    def auth_params(self) -> dict:
        """Return query-parameter dict to append to every Adzuna request."""
        if not self.is_configured:
            return {}
        return {"app_id": self.app_id, "app_key": self.api_key}


class IndeedAuthenticator:
    """Publisher API key authenticator for Indeed.

    Requires:
      INDEED_PUBLISHER_ID - publisher id from indeed.com/publisher
    """

    SEARCH_URL = "http://api.indeed.com/ads/apisearch"

    def __init__(self) -> None:
        settings = get_settings()
        self.publisher_id = settings.indeed_publisher_id

    @property
    def is_configured(self) -> bool:
        return bool(self.publisher_id)

    def get_credential(self) -> ApiKeyCredential | None:
        if not self.is_configured:
            logger.debug("Indeed publisher id not configured.")
            return None
        return ApiKeyCredential(app_id=self.publisher_id, api_key=self.publisher_id)

    def auth_params(self) -> dict:
        if not self.is_configured:
            return {}
        return {"publisher": self.publisher_id, "v": "2", "format": "json"}


class ZipRecruiterAuthenticator:
    """Bearer-token authenticator for ZipRecruiter Jobs API.

    Requires:
      ZIPRECRUITER_API_KEY — API key from app.ziprecruiter.com/partners
    """

    def __init__(self) -> None:
        settings = get_settings()
        self.api_key = settings.ziprecruiter_api_key

    @property
    def is_configured(self) -> bool:
        return bool(self.api_key)

    def auth_headers(self) -> dict:
        if not self.is_configured:
            return {}
        return {"Authorization": f"Bearer {self.api_key}"}


class GithubTokenAuthenticator:
    """Personal-access-token authenticator for GitHub Jobs via GH API.

    Requires:
      GITHUB_TOKEN — personal access token (optional; raises rate-limit without it)
    """

    def __init__(self) -> None:
        settings = get_settings()
        self.token = settings.github_token

    @property
    def is_configured(self) -> bool:
        return bool(self.token)

    def auth_headers(self) -> dict:
        base = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self.is_configured:
            base["Authorization"] = f"Bearer {self.token}"
        return base


# ---------------------------------------------------------------------------
# Session / cookie auth (browser-based boards)
# ---------------------------------------------------------------------------


class SessionAuthenticator:
    """Cookie / session-based authenticator for boards that expose login HTML.

    This is the fallback for sites that do not offer a clean API.  We post
    to their login form, store the session cookie and attach it to every
    subsequent request.

    Subclass and override ``LOGIN_URL``, ``_build_payload``.
    """

    LOGIN_URL: str = ""

    def __init__(self, username: str, password: str) -> None:
        self.username = username
        self.password = password
        self._session: aiohttp.ClientSession | None = None
        self._cookie_jar: aiohttp.CookieJar | None = None
        self._authenticated = False

    @property
    def is_configured(self) -> bool:
        return bool(self.username and self.password)

    def _build_payload(self) -> dict:
        """Override in subclasses to match target site's form fields."""
        return {"email": self.username, "password": self.password}

    async def authenticate(self) -> bool:
        """POST credentials to LOGIN_URL and retain session cookies."""
        if not self.is_configured or not self.LOGIN_URL:
            return False
        try:
            jar = aiohttp.CookieJar()
            session = aiohttp.ClientSession(cookie_jar=jar)
            resp = await session.post(
                self.LOGIN_URL,
                data=self._build_payload(),
                headers={"User-Agent": "Mozilla/5.0"},
                timeout=aiohttp.ClientTimeout(total=20),
                allow_redirects=True,
            )
            if resp.status in (200, 302):
                self._session = session
                self._cookie_jar = jar
                self._authenticated = True
                logger.info(f"Session auth successful for {self.LOGIN_URL}")
                return True
            else:
                await session.close()
                logger.warning(
                    f"Session auth failed [{resp.status}] for {self.LOGIN_URL}"
                )
        except Exception as exc:
            logger.error(f"Session auth error for {self.LOGIN_URL}: {exc}")
        return False

    def get_session(self) -> aiohttp.ClientSession | None:
        return self._session if self._authenticated else None

    async def close(self) -> None:
        if self._session:
            await self._session.close()
            self._session = None
            self._authenticated = False


# ---------------------------------------------------------------------------
# Central Auth Manager — singleton-like facade
# ---------------------------------------------------------------------------


class AuthManager:
    """Central façade that initialises and exposes all authenticators.

    Usage::

        auth = AuthManager()
        await auth.initialise()

        # For LinkedIn (OAuth)
        token = await auth.linkedin.get_token()

        # For Adzuna (API key)
        params = auth.adzuna.auth_params()
    """

    def __init__(self) -> None:
        self.linkedin = LinkedInAuthenticator()
        self.adzuna = AdzunaAuthenticator()
        self.indeed = IndeedAuthenticator()
        self.ziprecruiter = ZipRecruiterAuthenticator()
        self.github = GithubTokenAuthenticator()
        self._initialised = False

    async def initialise(self) -> None:
        """Run async auth steps (e.g. fetch OAuth tokens) at startup."""
        if self._initialised:
            return

        tasks = []

        if self.linkedin.is_configured:
            tasks.append(self.linkedin.get_token())

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

        self._initialised = True
        self._log_summary()

    def _log_summary(self) -> None:
        status = {
            "linkedin": self.linkedin.is_configured,
            "adzuna": self.adzuna.is_configured,
            "indeed": self.indeed.is_configured,
            "ziprecruiter": self.ziprecruiter.is_configured,
            "github": self.github.is_configured,
        }
        enabled = [k for k, v in status.items() if v]
        disabled = [k for k, v in status.items() if not v]
        if enabled:
            logger.info(f"AuthManager: authenticated sources → {enabled}")
        if disabled:
            logger.debug(f"AuthManager: unconfigured sources (skipped) → {disabled}")


# Module-level singleton
_auth_manager: AuthManager | None = None


async def get_auth_manager() -> AuthManager:
    """Return the singleton AuthManager, initialising it on first call."""
    global _auth_manager
    if _auth_manager is None:
        _auth_manager = AuthManager()
        await _auth_manager.initialise()
    return _auth_manager
