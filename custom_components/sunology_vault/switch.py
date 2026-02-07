"""Switch platform for Sunology VAULT."""

from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import SunologyDataUpdateCoordinator
from .entity import SunologyVaultEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up switches from config entry."""
    coordinator: SunologyDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities: list[SwitchEntity] = []

    for serial in coordinator.data.batteries:
        entities.append(SunologyPreserveEnergySwitch(coordinator, serial))

    async_add_entities(entities)


class SunologyPreserveEnergySwitch(SunologyVaultEntity, SwitchEntity):
    """Switch for battery preserve energy mode."""

    _attr_translation_key = "preserve_energy"

    def __init__(
        self, coordinator: SunologyDataUpdateCoordinator, serial: str
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator, serial)
        self._attr_unique_id = f"{serial}_preserve_energy"

    @property
    def is_on(self) -> bool | None:
        """Return true if preserve energy mode is on."""
        battery = self._battery_data
        if battery:
            return battery.preserve_energy
        return None

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on preserve energy mode."""
        await self.coordinator.async_set_preserve_energy(self._serial, True)

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off preserve energy mode."""
        await self.coordinator.async_set_preserve_energy(self._serial, False)
