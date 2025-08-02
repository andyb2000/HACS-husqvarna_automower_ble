"""The Husqvarna Autoconnect Bluetooth integration."""

from __future__ import annotations

import logging

import asyncio

from automower_ble.mower import Mower
from bleak import BleakError
from bleak_retry_connector import close_stale_connections_by_address, get_device

from homeassistant.components import bluetooth
from homeassistant.config_entries import ConfigEntry
#from homeassistant.const import CONF_ADDRESS, CONF_CLIENT_ID, Platform
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady

from .const import DOMAIN, CONF_ADDRESS, CONF_PIN, CONF_CLIENT_ID, STARTUP_MESSAGE
from .coordinator import HusqvarnaCoordinator

LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [
    Platform.LAWN_MOWER,
    Platform.SENSOR,
]

# Global lock and task to ensure connect() runs once
_connect_lock = asyncio.Lock()
_connect_task = None

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    global _connect_task
    """Set up Husqvarna Autoconnect Bluetooth from a config entry."""
    address = entry.data[CONF_ADDRESS]
    pin = entry.data[CONF_PIN]
    channel_id = entry.data[CONF_CLIENT_ID]

    LOGGER.info(STARTUP_MESSAGE)

    if pin != 0:
        mower = await asyncio.to_thread(Mower, channel_id, address, pin)
    else:
        mower = await asyncio.to_thread(Mower, channel_id, address)

    await close_stale_connections_by_address(address)

    LOGGER.debug("connecting to %s with channel ID %s and pin %s", address, str(channel_id), str(pin))
    device = bluetooth.async_ble_device_from_address(hass, address, connectable=True)
    if device is None:
        device = await get_device(address)

    async def do_connect():
        try:
            if not await mower.connect(device):
                raise ConfigEntryNotReady("Couldn't find device")
        except (BleakError, TimeoutError) as ex:
            raise ConfigEntryNotReady("Couldn't find device") from ex

        LOGGER.debug("connected and paired")
        return mower

    # Guard against parallel connection attempts
    async with _connect_lock:
        if _connect_task is None:
            _connect_task = asyncio.create_task(do_connect())

    mower = await _connect_task

    model = await mower.get_model()
    serial = await mower.command("GetSerialNumber")
    LOGGER.info("Connected to Automower: %s", model)

#    device_info = DeviceInfo(
#        identifiers={(DOMAIN, str(address) + str(channel_id))},
#        manufacturer=MANUFACTURER,
#        model=model,
#    )

    #coordinator = HusqvarnaCoordinator(hass, mower, device_info, address, model)
    coordinator = HusqvarnaCoordinator(hass, mower, address, model, channel_id, serial)

    await coordinator.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

#    LOGGER.debug("now trying to add extra sensors")
#    for platform in ["sensor"]:
#        hass.async_create_task(
#            hass.config_entries.async_forward_entry_setups(entry, platform)
#        )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        coordinator: HusqvarnaCoordinator = hass.data[DOMAIN].pop(entry.entry_id)
        await coordinator.async_shutdown()

    return unload_ok
