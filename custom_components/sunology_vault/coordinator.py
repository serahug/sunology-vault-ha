"""DataUpdateCoordinator for Sunology VAULT."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from datetime import timedelta
import logging

from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed, HomeAssistantError
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import ApiError, AuthenticationError, SunologyApiClient
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


def _get_or_default(data: dict, key: str, default):
    """Get value from dict, returning default if None or missing."""
    value = data.get(key)
    return value if value is not None else default


@dataclass
class BatteryData:
    """Data for a single battery."""

    serial: str
    name: str
    station_id: str = ""
    battery_level: int = 0
    battery_state: str = ""
    device_state: str = ""
    preserve_energy: bool = False
    threshold: int = 210


@dataclass
class SunologyData:
    """Data from Sunology API."""

    batteries: dict[str, BatteryData] = field(default_factory=dict)


class SunologyDataUpdateCoordinator(DataUpdateCoordinator[SunologyData]):
    """Coordinator to fetch data from Sunology API."""

    def __init__(
        self, hass: HomeAssistant, client: SunologyApiClient, scan_interval: int
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=scan_interval),
        )
        self.client = client
        self._data = SunologyData()

    def set_scan_interval(self, scan_interval: int) -> None:
        """Update the scan interval."""
        self.update_interval = timedelta(seconds=scan_interval)

    async def _async_update_data(self) -> SunologyData:
        """Fetch data from API."""
        try:
            stations = await self.client.async_get_stations()
            overview = await self.client.async_get_overview()

            # Fetch all station details in parallel
            details_tasks = [
                self.client.async_get_station_details(station["id"])
                for station in stations
            ]
            all_details = await asyncio.gather(*details_tasks)

            panels = overview.get("production", {}).get("panels", {})

            for station, details in zip(stations, all_details):
                serial = station["serialNumber"]
                station_id = station["id"]
                name = station.get("name", serial)

                panel_data = panels.get(serial, {})
                current_level = panel_data.get("battery", 0)
                battery_state = panel_data.get("batteryState", "")
                device_state = panel_data.get("deviceState", "")

                preserve_energy = _get_or_default(details, "batteryPreserveEnergy", False)
                threshold = _get_or_default(details, "batteryThreshold", 210)

                if serial not in self._data.batteries:
                    self._data.batteries[serial] = BatteryData(
                        serial=serial,
                        name=name,
                        station_id=station_id,
                        battery_level=current_level,
                        battery_state=battery_state,
                        device_state=device_state,
                        preserve_energy=preserve_energy,
                        threshold=threshold,
                    )
                else:
                    battery = self._data.batteries[serial]
                    battery.name = name
                    battery.station_id = station_id
                    battery.battery_level = current_level
                    battery.battery_state = battery_state
                    battery.device_state = device_state
                    battery.preserve_energy = preserve_energy
                    battery.threshold = threshold

            return self._data

        except AuthenticationError as err:
            raise ConfigEntryAuthFailed from err
        except ApiError as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err

    async def async_set_preserve_energy(self, serial: str, value: bool) -> None:
        """Set preserve energy mode."""
        battery = self._data.batteries.get(serial)
        if not battery:
            raise HomeAssistantError(f"Battery {serial} not found")
        try:
            # GET current state to avoid overwriting stale values
            details = await self.client.async_get_station_details(battery.station_id)
            current_threshold = _get_or_default(details, "batteryThreshold", battery.threshold)

            response = await self.client.async_update_station(
                battery.station_id,
                battery.serial,
                battery.name,
                preserve_energy=value,
                threshold=current_threshold,
            )
            # Update local state from API response
            if response.get("batteryPreserveEnergy") is not None:
                battery.preserve_energy = response["batteryPreserveEnergy"]
            if response.get("batteryThreshold") is not None:
                battery.threshold = response["batteryThreshold"]
            self.async_set_updated_data(self._data)
        except ApiError as err:
            _LOGGER.error("Failed to set preserve energy for %s: %s", serial, err)
            raise HomeAssistantError(f"Failed to update setting: {err}") from err

    async def async_set_threshold(self, serial: str, value: int) -> None:
        """Set charge threshold."""
        battery = self._data.batteries.get(serial)
        if not battery:
            raise HomeAssistantError(f"Battery {serial} not found")
        try:
            # GET current state to avoid overwriting stale values
            details = await self.client.async_get_station_details(battery.station_id)
            current_preserve = _get_or_default(details, "batteryPreserveEnergy", battery.preserve_energy)

            response = await self.client.async_update_station(
                battery.station_id,
                battery.serial,
                battery.name,
                preserve_energy=current_preserve,
                threshold=value,
            )
            # Update local state from API response
            if response.get("batteryPreserveEnergy") is not None:
                battery.preserve_energy = response["batteryPreserveEnergy"]
            if response.get("batteryThreshold") is not None:
                battery.threshold = response["batteryThreshold"]
            self.async_set_updated_data(self._data)
        except ApiError as err:
            _LOGGER.error("Failed to set threshold for %s: %s", serial, err)
            raise HomeAssistantError(f"Failed to update setting: {err}") from err
