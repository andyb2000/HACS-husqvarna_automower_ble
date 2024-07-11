"""Support for Husqvarna BLE sensors."""

from __future__ import annotations

import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE,UnitOfLength,UnitOfTime
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER
from .coordinator import HusqvarnaAutomowerBleEntity, HusqvarnaCoordinator

_LOGGER = logging.getLogger(__name__)

MOWER_SENSORS = [
    {
        "name": "Battery Level",
        "query_key": "battery_level",
        "unit": PERCENTAGE,
        "device_class": SensorDeviceClass.BATTERY,
        "state_class": None,
        "sensor_class": SensorStateClass.MEASUREMENT,
        "entity_category": None,
        "sensor_icon": "mdi:battery",
        "description": "Mower battery level",
    },
    {
        "name": "Next Start Time",
        "query_key": "next_start_time",
        "unit": None,
        "device_class": None,
        "state_class": None,
        "sensor_class": None,
        "entity_category": None,
        "sensor_icon": "mdi:timer",
        "description": "Mower next start time",
    },
    {
        "name": "Total running time",
        "query_key": "statistics[totalRunningTime]",
        "unit": UnitOfTime.SECONDS,
        "device_class": SensorDeviceClass.DURATION,
        "state_class": SensorStateClass.TOTAL,
        "sensor_class": None,
        "entity_category": EntityCategory.DIAGNOSTIC,
        "sensor_icon": "mdi:timer",
        "description": "Mowers total running time",
    },
    {
        "name": "Total cutting time",
        "query_key": "totalCuttingTime",
        "unit": UnitOfTime.SECONDS,
        "device_class": SensorDeviceClass.DURATION,
        "state_class": SensorStateClass.TOTAL,
        "sensor_class": None,
        "entity_category": EntityCategory.DIAGNOSTIC,
        "sensor_icon": "mdi:timer",
        "description": "Mowers total cutting time",
    },
    {
        "name": "Total charging time",
        "query_key": "totalChargingTime",
        "unit": UnitOfTime.SECONDS,
        "device_class": SensorDeviceClass.DURATION,
        "state_class": SensorStateClass.TOTAL,
        "sensor_class": None,
        "entity_category": EntityCategory.DIAGNOSTIC,
        "sensor_icon": "mdi:timer",
        "description": "Mowers total charging time",
    },
    {
        "name": "Total searcing time",
        "query_key": "totalSearchingTime",
        "unit": UnitOfTime.SECONDS,
        "device_class": SensorDeviceClass.DURATION,
        "state_class": SensorStateClass.TOTAL,
        "sensor_class": None,
        "entity_category": EntityCategory.DIAGNOSTIC,
        "sensor_icon": "mdi:timer",
        "description": "Mowers total searing for base time",
    },
    {
        "name": "Total number of collisions",
        "query_key": "numberOfCollisions",
        "unit": None,
        "device_class": None,
        "state_class": SensorStateClass.TOTAL,
        "sensor_class": None,
        "entity_category": EntityCategory.DIAGNOSTIC,
        "sensor_icon": "mdi:crash",
        "description": "Mowers number of collisions",
    },
    {
        "name": "Total number of charging cycles",
        "query_key": "numberOfChargingCycles",
        "unit": None,
        "device_class": None,
        "state_class": SensorStateClass.TOTAL,
        "sensor_class": None,
        "entity_category": EntityCategory.DIAGNOSTIC,
        "sensor_icon": "mdi:charge",
        "description": "Mowers total number of charge cycles",
    },
    {
        "name": "Total cutting blade usage",
        "query_key": "totalChargingTime",
        "unit": UnitOfTime.SECONDS,
        "device_class": SensorDeviceClass.DURATION,
        "state_class": SensorStateClass.TOTAL,
        "sensor_class": None,
        "entity_category": EntityCategory.DIAGNOSTIC,
        "sensor_icon": "mdi:blade",
        "description": "Mowers total blade usage time",
    },
]

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up AutomowerLawnMower sensor from a config entry."""
    coordinator: HusqvarnaCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    _LOGGER.debug("Creating mower sensors")
    sensors = [AutomowerSensorEntity(coordinator, sensor_config) for sensor_config in MOWER_SENSORS]
    _LOGGER.debug("About to add sensors: " + str(sensors))
    if not sensors:
        _LOGGER.error("No sensors were created. Check SENSOR_CONFIG.")
    async_add_entities(sensors)

class AutomowerSensorEntity(CoordinatorEntity, SensorEntity):

    def __init__(self,coordinator: HusqvarnaCoordinator,config) -> None:
        """Set up AutomowerSensors."""
        super().__init__(coordinator)
        self._name = config["name"]
        self._query_key = config["query_key"]
        self._unit_of_measurement = config["unit"]
        self._device_class = config["device_class"]
        self._state = config["state_class"]
        self._sensor_class = config["sensor_class"]
        self._entity_category = config["entity_category"]
        self._description = config["description"]
        self._attributes = {"description": self._description}

        _LOGGER.debug("in AutomowerSensorEntity creating entity for: " + str(self._name))

#        super().__init__(coordinator)
#        self._update_attr()

    @property
    def name(self):
        """Return the name of the sensor."""
        return self._name

    @property
    def state(self):
        """Return the state of the sensor."""
        data = self.coordinator.data
        if data:
            _LOGGER.debug("state of sensor data structure: " + str(data))
            value = data.get(self._query_key)
            if value:
                _LOGGER.debug("value of sensor data structure: " + str(value))
                return value
        return None

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this sensor."""
        return self._unit_of_measurement

    @property
    def device_class(self):
        """Return the device class of this sensor."""
        return self._device_class

    @property
    def sensor_class(self):
        """Return the sensor class of this sensor."""
        return self._sensor_class

    @property
    def extra_state_attributes(self):
        """Return the state attributes."""
        return self._attributes

    @property
    def entity_category(self):
        """Return the entity category of this sensor."""
        return self._entity_category

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle coordinator update."""
        self._update_attr()
        super()._handle_coordinator_update()

    @callback
    def _update_attr(self) -> None:
        """Update attributes for sensor."""
        self._attr_native_value = None
        try:
            self._attr_native_value = self.coordinator.data[self._query_key]
            self._attr_available = self._attr_native_value is not None
            _LOGGER.debug("Update sensor %s with value %s", self._query_key, self._attr_native_value)
            return self._attr_native_value
        except KeyError:
            self._attr_native_value = None
            _LOGGER.error(
                "%s not a valid attribute (in _update_attr)",
                self._query_key,
            )

    async def async_update(self):
        """Update attributes for sensor."""
        self._attr_native_value = None
        try:
            self._attr_native_value = self.coordinator.data[self._query_key]
            self._attr_available = self._attr_native_value is not None
            _LOGGER.debug("Update sensor %s with value %s", self._query_key, self._attr_native_value)
        except KeyError:
            self._attr_native_value = None
            _LOGGER.error(
                "%s not a valid attribute (in async_update)",
                self._query_key,
            )
