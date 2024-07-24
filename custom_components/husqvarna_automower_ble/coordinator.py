"""Provides the DataUpdateCoordinator."""

from __future__ import annotations

from datetime import timedelta, datetime
import logging
from typing import Any

from automower_ble.mower import Mower
from bleak import BleakError
from bleak_retry_connector import close_stale_connections_by_address

from homeassistant.components import bluetooth
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(seconds=60)


class HusqvarnaCoordinator(DataUpdateCoordinator[dict[str, bytes]]):
    """Class to manage fetching data."""

    def __init__(
        self,
        hass: HomeAssistant,
        mower: Mower,
        address: str,
        model: str,
        channel_id: str,
        serial: str,
    ) -> None:
        """Initialize global data updater."""
        super().__init__(
            hass=hass,
            logger=_LOGGER,
            name=DOMAIN,
            update_interval=SCAN_INTERVAL,
        )
        self.address = address
        self.model = model
        self.mower = mower
        self.channel_id = channel_id
        self.serial = serial
        self._last_successful_update = None
        self._last_data = None

    async def async_shutdown(self) -> None:
        """Shutdown coordinator and any connection."""
        _LOGGER.debug("Shutdown")
        await super().async_shutdown()
        if self.mower.is_connected():
            await self.mower.disconnect()

    async def _async_find_device(self):
        _LOGGER.debug("Trying to reconnect")
        await close_stale_connections_by_address(self.address)

        device = bluetooth.async_ble_device_from_address(
            self.hass, self.address, connectable=True
        )
        if not device:
            _LOGGER.error("Can't find device")
            raise UpdateFailed("Can't find device")

        try:
            if not await self.mower.connect(device):
                raise UpdateFailed("Failed to connect")
        except (TimeoutError, BleakError) as ex:
            raise UpdateFailed("Failed to connect") from ex

    async def _async_update_data(self) -> dict[str, bytes]:
        """Poll the device."""
        _LOGGER.debug("Polling device")

        data: dict[str, bytes] = {}

        try:
            if not self.mower.is_connected():
                await self._async_find_device()
        except (TimeoutError, BleakError) as ex:
            raise UpdateFailed("Failed to connect") from ex

        try:
            data["battery_level"] = await self.mower.battery_level()
            _LOGGER.debug("battery level: " + str(data["battery_level"]))
#            if data["battery_level"] is None:
#                await self._async_find_device()
#                raise UpdateFailed("Error getting data from device")

            data["activity"] = await self.mower.mower_activity()
            _LOGGER.debug("activity: " + str(data["activity"]))
#            if data["activity"] is None:
#                await self._async_find_device()
#                raise UpdateFailed("Error getting data from device")

            data["state"] = await self.mower.mower_state()
            _LOGGER.debug("state: " + str(data["state"]))
#            if data["state"] is None:
#                await self._async_find_device()
#                raise UpdateFailed("Error getting data from device")

            data["next_start_time"] = await self.mower.mower_next_start_time()
            _LOGGER.debug("next_start_time: " + str(data["next_start_time"]))
#            if data["next_start_time"] is None:
#                await self._async_find_device()
#                raise UpdateFailed("Error getting data from device")

            data["errorCode"] = await self.mower.command("GetError")
            _LOGGER.debug("errorCode: " + str(data["errorCode"]))

            data["NumberOfMessages"] = await self.mower.command("GetNumberOfMessages")
            _LOGGER.debug("NumberOfMessages: " + str(data["NumberOfMessages"]))

            data["RemainingChargingTime"] = await self.mower.command("GetRemainingChargingTime")
            _LOGGER.debug("RemainingChargingTime: " + str(data["RemainingChargingTime"]))

            data["statistics"] = await self.mower.command("GetAllStatistics")
            _LOGGER.debug("statuses: " + str(data["statistics"]))

            data["operatorstate"] = await self.mower.command("IsOperatorLoggedIn")
            _LOGGER.debug("IsOperatorLoggedIn: " + str(data["operatorstate"]))

            data["last_message"] = await mower.command("GetMessage", messageId=0)
            _LOGGER.debug("last_message: " + str(data["last_message"]))

            self._last_successful_update = datetime.now()
            self._last_data = data

        except (TimeoutError, BleakError) as ex:
            _LOGGER.error("Error getting data from device")
            if self._last_data and (datetime.now() - self._last_successful_update < timedelta(hours=1)):
                _LOGGER.debug("Failed to fetch data, using last known good values from the past 1hr")
                return self._last_data
            else:
                await self._async_find_device()
                raise UpdateFailed("Error getting data from device") from ex

        _LOGGER.debug("return from coordinator with data")
        return data


class HusqvarnaAutomowerBleEntity(CoordinatorEntity[HusqvarnaCoordinator]):
    """Coordinator entity for Husqvarna Automower Bluetooth."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: HusqvarnaCoordinator, context: Any = None) -> None:
        """Initialize coordinator entity."""
        super().__init__(coordinator, context)

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return self.coordinator.mower.is_connected()
