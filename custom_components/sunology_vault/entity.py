"""Base entity for Sunology VAULT."""

from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import BatteryData, SunologyDataUpdateCoordinator


class SunologyVaultEntity(CoordinatorEntity[SunologyDataUpdateCoordinator]):
    """Base class for Sunology VAULT entities."""

    _attr_has_entity_name = True
    _available_when_unplugged = False

    def __init__(
        self, coordinator: SunologyDataUpdateCoordinator, serial: str
    ) -> None:
        """Initialize the entity."""
        super().__init__(coordinator)
        self._serial = serial
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, serial)},
            name=coordinator.data.batteries[serial].name,
            serial_number=serial,
            manufacturer="Sunology",
            model="VAULT",
        )

    @property
    def _battery_data(self) -> BatteryData | None:
        """Get battery data for this entity."""
        return self.coordinator.data.batteries.get(self._serial)

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        if not super().available:
            return False
        battery = self._battery_data
        if battery is None or battery.device_state != "CONNECTED":
            return False
        if not self._available_when_unplugged and battery.battery_state == "UNPLUGGED":
            return False
        return True
