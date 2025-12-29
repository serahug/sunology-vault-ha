"""Number platform for Sunology VAULT."""

from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfPower
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import SunologyDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up number entities from config entry."""
    coordinator: SunologyDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[NumberEntity] = []

    for serial in coordinator.data.batteries:
        entities.append(SunologyThresholdNumber(coordinator, serial))

    async_add_entities(entities)


class SunologyThresholdNumber(
    CoordinatorEntity[SunologyDataUpdateCoordinator], NumberEntity
):
    """Number entity for battery charge threshold."""

    _attr_has_entity_name = True
    _attr_translation_key = "charge_threshold"
    _attr_native_min_value = 210
    _attr_native_max_value = 450
    _attr_native_step = 10
    _attr_native_unit_of_measurement = UnitOfPower.WATT
    _attr_mode = NumberMode.SLIDER

    def __init__(
        self, coordinator: SunologyDataUpdateCoordinator, serial: str
    ) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator)
        self._serial = serial
        self._attr_unique_id = f"{serial}_threshold"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, serial)},
            "name": f"{coordinator.data.batteries[serial].name} ({serial})",
            "manufacturer": "Sunology",
            "model": "VAULT",
        }

    @property
    def _battery_data(self):
        """Get battery data for this entity."""
        return self.coordinator.data.batteries.get(self._serial)

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        battery = self._battery_data
        return battery is not None and battery.device_state == "CONNECTED"

    @property
    def native_value(self) -> int | None:
        """Return the current threshold value."""
        if self._battery_data:
            return self._battery_data.threshold
        return None

    async def async_set_native_value(self, value: float) -> None:
        """Set the threshold value."""
        await self.coordinator.async_set_threshold(self._serial, int(value))
