"""Sunology API client."""

import asyncio
import json
import logging
from typing import Any

import aiohttp

from .const import API_HEADERS, BASE_URL

_LOGGER = logging.getLogger(__name__)

RETRY_ATTEMPTS = 2
RETRY_DELAY = 1


def _mask_sensitive_data(data: dict | None, keys_to_mask: set[str]) -> dict | None:
    """Mask sensitive data in a dictionary for logging."""
    if data is None:
        return None
    masked = dict(data)
    for key in keys_to_mask:
        if key in masked:
            masked[key] = "***MASKED***"
    return masked


def _format_json(data: Any) -> str:
    """Format data as indented JSON for logging."""
    try:
        return json.dumps(data, indent=2, ensure_ascii=False)
    except (TypeError, ValueError):
        return str(data)


class AuthenticationError(Exception):
    """Authentication error."""


class ApiError(Exception):
    """API error."""


class SunologyApiClient:
    """Async client for Sunology API."""

    def __init__(self, email: str, password: str) -> None:
        """Initialize the client."""
        self._email = email
        self._password = password
        self._session_token: str | None = None
        self._session: aiohttp.ClientSession | None = None

    async def _get_session(self) -> aiohttp.ClientSession:
        """Get or create the aiohttp session."""
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=30)
            )
        return self._session

    async def async_close(self) -> None:
        """Close the aiohttp session."""
        if self._session and not self._session.closed:
            await self._session.close()
            self._session = None

    async def async_login(self) -> bool:
        """Authenticate and store session token."""
        url = f"{BASE_URL}/api/login-post"
        body = {"username": self._email, "password": self._password}
        masked_body = _mask_sensitive_data(body, {"password"})

        _LOGGER.debug(
            "[API] >>> POST %s\n[API] Request body:\n%s",
            url,
            _format_json(masked_body),
        )

        try:
            session = await self._get_session()
            async with session.post(
                url,
                json=body,
                headers=API_HEADERS,
            ) as resp:
                _LOGGER.debug(
                    "[API] <<< Response: %s %s",
                    resp.status,
                    resp.reason,
                )
                if resp.cookies:
                    _LOGGER.debug(
                        "[API] Cookies received: %s",
                        ", ".join(f"{k}=***" for k in resp.cookies.keys()),
                    )

                if resp.status == 204:
                    cookie = resp.cookies.get("SESSION")
                    if cookie:
                        self._session_token = cookie.value
                        self._password = ""
                        _LOGGER.debug("[API] Login successful, session token stored")
                        return True
                    raise AuthenticationError("No session cookie in response")
                if resp.status == 401:
                    raise AuthenticationError("Invalid credentials")
                raise ApiError(f"Login failed: {resp.status}")
        except AuthenticationError:
            raise
        except (aiohttp.ClientError, asyncio.TimeoutError) as err:
            _LOGGER.debug("[API] Network error: %s", err)
            raise ApiError(f"Network error: {err}") from err

    async def async_get_stations(self) -> list[dict[str, Any]]:
        """Get list of stations."""
        return await self._async_request("GET", "/api/devices/stations-and-storages")

    async def async_get_overview(self) -> dict[str, Any]:
        """Get real-time overview data."""
        return await self._async_request(
            "POST",
            "/api/overview",
            json_data={"storages": [], "streamMeters": [], "erls": []},
        )

    async def async_get_station_details(self, station_id: str) -> dict[str, Any]:
        """Get detailed info for a station."""
        return await self._async_request("GET", f"/api/solar-panels/{station_id}")

    async def async_update_station(
        self,
        station_id: str,
        serial_number: str,
        name: str,
        preserve_energy: bool | None = None,
        threshold: int | None = None,
    ) -> dict[str, Any]:
        """Update station settings."""
        data: dict[str, Any] = {
            "id": station_id,
            "serialNumber": serial_number,
            "name": name,
        }
        if preserve_energy is not None:
            data["batteryPreserveEnergy"] = preserve_energy
        if threshold is not None:
            data["batteryThreshold"] = str(threshold)

        return await self._async_request(
            "PATCH",
            f"/api/solar-panels/{station_id}",
            json_data=data,
        )

    async def _async_request(
        self,
        method: str,
        endpoint: str,
        json_data: dict[str, Any] | None = None,
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Make authenticated API request with retry for transient errors."""
        if not self._session_token:
            raise AuthenticationError("Not authenticated")

        url = f"{BASE_URL}{endpoint}"
        headers = {**API_HEADERS, "Cookie": f"SESSION={self._session_token}"}

        last_err: Exception | None = None
        for attempt in range(1, RETRY_ATTEMPTS + 1):
            # Log request details
            _LOGGER.debug("[API] >>> %s %s (attempt %s)", method, url, attempt)
            if json_data:
                _LOGGER.debug("[API] Request body:\n%s", _format_json(json_data))

            try:
                session = await self._get_session()
                async with session.request(
                    method,
                    url,
                    headers=headers,
                    json=json_data,
                ) as resp:
                    # Log response status
                    _LOGGER.debug(
                        "[API] <<< Response: %s %s",
                        resp.status,
                        resp.reason,
                    )

                    if resp.status == 401:
                        _LOGGER.debug("[API] Session expired (401)")
                        raise AuthenticationError("Session expired")
                    if resp.status >= 400:
                        body_text = await resp.text()
                        _LOGGER.debug("[API] Error response body:\n%s", body_text)
                        raise ApiError(f"API error: {resp.status}")

                    response_data = await resp.json()
                    _LOGGER.debug(
                        "[API] Response body:\n%s",
                        _format_json(response_data),
                    )
                    return response_data
            except (AuthenticationError, ApiError):
                raise
            except (aiohttp.ClientError, asyncio.TimeoutError) as err:
                last_err = err
                _LOGGER.debug(
                    "[API] Transient error (attempt %s/%s): %s",
                    attempt,
                    RETRY_ATTEMPTS,
                    err,
                )
                if attempt < RETRY_ATTEMPTS:
                    await asyncio.sleep(RETRY_DELAY)

        raise ApiError(f"Network error: {last_err}") from last_err
