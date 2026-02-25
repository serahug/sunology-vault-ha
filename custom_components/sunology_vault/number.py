"""Number platform for Sunology VAULT."""

from __future__ import annotations

from homeassistant.components.number import NumberDeviceClass, NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfPower
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, MAX_THRESHOLD, MIN_THRESHOLD
from .coordinator import SunologyDataUpdateCoordinator
from .entity import SunologyVaultEntity


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


class SunologyThresholdNumber(SunologyVaultEntity, NumberEntity):
    """Number entity for battery charge threshold."""

    _attr_device_class = NumberDeviceClass.POWER
    _attr_translation_key = "charge_threshold"
    _attr_native_min_value = MIN_THRESHOLD
    _attr_native_max_value = MAX_THRESHOLD
    _attr_native_step = 10
    _attr_native_unit_of_measurement = UnitOfPower.WATT
    _attr_mode = NumberMode.SLIDER
    _available_when_unplugged = True

    def __init__(
        self, coordinator: SunologyDataUpdateCoordinator, serial: str
    ) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator, serial)
        self._attr_unique_id = f"{serial}_threshold"

    @property
    def native_value(self) -> int | None:
        """Return the current threshold value."""
        battery = self._battery_data
        if battery:
            return battery.threshold
        return None

    async def async_set_native_value(self, value: float) -> None:
        """Set the threshold value."""
        await self.coordinator.async_set_threshold(self._serial, int(value))
