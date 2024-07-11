"""Demo platform that has a couple fake lawn mowers."""

from __future__ import annotations

import logging

from homeassistant.components import bluetooth
from homeassistant.components.lawn_mower import (
    LawnMowerActivity,
    LawnMowerEntity,
    LawnMowerEntityFeature,
)
from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from datetime import datetime

from .const import DOMAIN, MANUFACTURER
from .coordinator import HusqvarnaAutomowerBleEntity, HusqvarnaCoordinator

_LOGGER = logging.getLogger(__name__)

FEATURES = (
    LawnMowerEntityFeature.PAUSE
    | LawnMowerEntityFeature.START_MOWING
    | LawnMowerEntityFeature.DOCK
)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up AutomowerLawnMower integration from a config entry."""
    coordinator: HusqvarnaCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    model = coordinator.model
    address = coordinator.address

    async_add_entities(
        [
            AutomowerLawnMower(
                coordinator,
                "automower" + model + "_" + address,
                model,
                FEATURES,
            ),
        ]
    )

class AutomowerLawnMower(HusqvarnaAutomowerBleEntity, LawnMowerEntity):
    """Husqvarna Automower."""

    def __init__(
        self,
        coordinator: Coordinator,
        unique_id: str,
        name: str,
        features: LawnMowerEntityFeature = LawnMowerEntityFeature(0),
    ) -> None:
        """Initialize the lawn mower."""
        super().__init__(coordinator)
        self._attr_name = name
        self._attr_unique_id = unique_id
        self._attr_supported_features = features
        self._attr_activity = LawnMowerActivity.ERROR
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, coordinator.serial)},
            manufacturer=MANUFACTURER,
            model=coordinator.model,
        )

    def _get_activity(self) -> LawnMowerActivity | None:
        """Return the current lawn mower activity."""
        if self.coordinator.data is None:
            return None

        state = str(self.coordinator.data["state"])
        activity = str(self.coordinator.data["activity"])

        _LOGGER.debug("mower state = " + state)
        _LOGGER.debug("mower activity = " + activity)

        if state is None or activity is None:
            return None
        match state:
            case "5":
                return LawnMowerActivity.PAUSED
            case "2" | "0" | "1":
                return LawnMowerActivity.ERROR
            case "7" | "6" | "4":
                match activity:
                    case "1" | "5":
                        return LawnMowerActivity.DOCKED
                    case "2" | "3" | "4":
                        return LawnMowerActivity.MOWING 
        return LawnMowerActivity.ERROR

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""
        _LOGGER.debug("AutomowerLawnMower: _handle_coordinator_update")
        self._update_attr()
        super()._handle_coordinator_update()

    @callback
    def _update_attr(self) -> None:
        self._attr_activity = self._get_activity()
        self._attr_available = self._attr_activity is not None

    async def async_start_mowing(self) -> None:
        """Start mowing."""
        _LOGGER.debug("Starting mower")

        if not self.coordinator.mower.is_connected():
            device = bluetooth.async_ble_device_from_address(
                self.coordinator.hass, self.coordinator.address, connectable=True
            )
            if not await self.coordinator.mower.connect(device):
                return

        await self.coordinator.mower.mower_resume()
        if self._attr_activity == LawnMowerActivity.DOCKED:
            await self.coordinator.mower.mower_override()
        await self.coordinator.async_request_refresh()

        self._attr_activity = self._get_activity()
        self.async_write_ha_state()

    async def async_dock(self) -> None:
        """Start docking."""
        _LOGGER.debug("Start docking")

        if not self.coordinator.mower.is_connected():
            device = bluetooth.async_ble_device_from_address(
                self.coordinator.hass, self.coordinator.address, connectable=True
            )
            if not await self.coordinator.mower.connect(device):
                return

        await self.coordinator.mower.mower_park()
        await self.coordinator.async_request_refresh()

        self._attr_activity = self._get_activity()
        self.async_write_ha_state()

    async def async_pause(self) -> None:
        """Pause mower."""
        _LOGGER.debug("Pausing mower")

        if not self.coordinator.mower.is_connected():
            device = bluetooth.async_ble_device_from_address(
                self.coordinator.hass, self.coordinator.address, connectable=True
            )
            if not await self.coordinator.mower.connect(device):
                return

        await self.coordinator.mower.mower_pause()
        await self.coordinator.async_request_refresh()

        self._attr_activity = self._get_activity()
        self.async_write_ha_state()

