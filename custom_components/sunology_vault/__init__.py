"""Sunology VAULT integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed, ConfigEntryNotReady

from .api import ApiError, AuthenticationError, SunologyApiClient
from .const import CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL, DOMAIN
from .coordinator import SunologyDataUpdateCoordinator

PLATFORMS = [Platform.NUMBER, Platform.SENSOR, Platform.SWITCH]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Sunology VAULT from config entry."""
    client = SunologyApiClient(
        entry.data[CONF_EMAIL],
        entry.data[CONF_PASSWORD],
    )

    try:
        await client.async_login()
    except AuthenticationError as err:
        await client.async_close()
        raise ConfigEntryAuthFailed(err) from err
    except ApiError as err:
        await client.async_close()
        raise ConfigEntryNotReady(err) from err

    scan_interval = entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
    coordinator = SunologyDataUpdateCoordinator(hass, client, scan_interval)
    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception:
        await client.async_close()
        raise

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    entry.async_on_unload(entry.add_update_listener(_async_update_listener))

    return True


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Handle options update."""
    coordinator: SunologyDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    scan_interval = entry.options.get(CONF_SCAN_INTERVAL, DEFAULT_SCAN_INTERVAL)
    coordinator.set_scan_interval(scan_interval)


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        coordinator: SunologyDataUpdateCoordinator = hass.data[DOMAIN].pop(entry.entry_id)
        await coordinator.client.async_close()
    return unload_ok
