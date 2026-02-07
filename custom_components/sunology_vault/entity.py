"""Base entity for Sunology VAULT."""

from __future__ import annotations

from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import BatteryData, SunologyDataUpdateCoordinator


class SunologyVaultEntity(CoordinatorEntity[SunologyDataUpdateCoordinator]):
    """Base class for Sunology VAULT entities."""

    _attr_has_entity_name = True

    def __init__(
        self, coordinator: SunologyDataUpdateCoordinator, serial: str
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self._serial = serial
        self._attr_device_info = {
            "identifiers": {(DOMAIN, serial)},
            "name": f"{coordinator.data.batteries[serial].name} ({serial})",
            "manufacturer": "Sunology",
            "model": "VAULT",
        }

    @property
    def _battery_data(self) -> BatteryData | None:
        """Get battery data for this entity."""
        return self.coordinator.data.batteries.get(self._serial)

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        battery = self._battery_data
        return battery is not None and battery.device_state == "CONNECTED"
