"""Sensor platform for Sunology VAULT."""

from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfEnergy
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import BATTERY_CAPACITY_WH, DOMAIN
from .coordinator import SunologyDataUpdateCoordinator
from .entity import SunologyVaultEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up sensors from config entry."""
    coordinator: SunologyDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[SensorEntity] = []

    for serial in coordinator.data.batteries:
        entities.append(SunologyBatteryLevelSensor(coordinator, serial))
        entities.append(SunologyBatteryStateSensor(coordinator, serial))
        entities.append(SunologyBatteryEnergySensor(coordinator, serial))

    async_add_entities(entities)


class SunologyBatteryLevelSensor(SunologyVaultEntity, SensorEntity):
    """Battery level percentage sensor."""

    _attr_device_class = SensorDeviceClass.BATTERY
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_translation_key = "battery_level"

    def __init__(
        self, coordinator: SunologyDataUpdateCoordinator, serial: str
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, serial)
        self._attr_unique_id = f"{serial}_battery_level"

    @property
    def native_value(self) -> int | None:
        """Return the battery level."""
        battery = self._battery_data
        if battery:
            return battery.battery_level
        return None


class SunologyBatteryStateSensor(SunologyVaultEntity, SensorEntity):
    """Battery state sensor."""

    _available_when_unplugged = True
    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options = ["off", "charging", "discharging", "unplugged"]
    _attr_translation_key = "battery_state"

    def __init__(
        self, coordinator: SunologyDataUpdateCoordinator, serial: str
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, serial)
        self._attr_unique_id = f"{serial}_battery_state"

    @property
    def native_value(self) -> str | None:
        """Return the battery state."""
        battery = self._battery_data
        if battery and battery.battery_state:
            return battery.battery_state.lower()
        return None

    @property
    def icon(self) -> str:
        """Return icon based on battery state."""
        state = self.native_value
        if state == "charging":
            return "mdi:battery-charging"
        if state == "discharging":
            return "mdi:battery-arrow-down"
        if state == "unplugged":
            return "mdi:battery-remove-outline"
        return "mdi:battery-off"


class SunologyBatteryEnergySensor(SunologyVaultEntity, SensorEntity):
    """Battery available energy sensor."""

    _attr_device_class = SensorDeviceClass.ENERGY_STORAGE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfEnergy.WATT_HOUR
    _attr_translation_key = "battery_energy"

    def __init__(
        self, coordinator: SunologyDataUpdateCoordinator, serial: str
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, serial)
        self._attr_unique_id = f"{serial}_battery_energy"

    @property
    def native_value(self) -> int | None:
        """Return the available energy in Wh."""
        battery = self._battery_data
        if battery:
            return int(battery.battery_level * BATTERY_CAPACITY_WH / 100)
        return None
