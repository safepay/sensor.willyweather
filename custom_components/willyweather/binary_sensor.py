"""Support for WillyWeather binary sensors."""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from .const import (
    ATTRIBUTION,
    CONF_INCLUDE_WARNINGS,
    CONF_STATION_ID,
    CONF_STATION_NAME,
    DOMAIN,
    MANUFACTURER,
    WARNING_BINARY_SENSOR_TYPES,
)
from .coordinator import WillyWeatherDataUpdateCoordinator

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up WillyWeather binary sensor based on a config entry."""
    coordinator: WillyWeatherDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []
    
    station_id = entry.data[CONF_STATION_ID]
    station_name = entry.data.get(CONF_STATION_NAME, f"Station {station_id}")

    # Add warning sensors if enabled
    if entry.options.get(CONF_INCLUDE_WARNINGS, False):
        for sensor_type in WARNING_BINARY_SENSOR_TYPES:
            entities.append(
                WillyWeatherWarningBinarySensor(
                    coordinator,
                    station_id,
                    station_name,
                    sensor_type,
                )
            )

    async_add_entities(entities)


class WillyWeatherWarningBinarySensor(CoordinatorEntity, BinarySensorEntity):
    """Implementation of a WillyWeather warning binary sensor."""

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: WillyWeatherDataUpdateCoordinator,
        station_id: str,
        station_name: str,
        sensor_type: str,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self._sensor_type = sensor_type
        self._station_id = station_id
        self._station_name = station_name

        sensor_info = WARNING_BINARY_SENSOR_TYPES[sensor_type]
        self._attr_name = sensor_info["name"]
        self._attr_unique_id = f"{station_id}_{sensor_type}"
        self._attr_icon = sensor_info["icon"]
        self._attr_device_class = sensor_info.get("device_class")

        self._attr_device_info = DeviceInfo(
            entry_type=DeviceEntryType.SERVICE,
            identifiers={(DOMAIN, f"{station_id}_binary_sensors")},
            manufacturer=MANUFACTURER,
            name=f"{station_name} Binary Sensors",
            via_device=(DOMAIN, station_id),
        )

    @property
    def is_on(self) -> bool | None:
        """Return True if warning is active."""
        if not self.coordinator.data:
            return None

        warning_data = self.coordinator.data.get("warnings", {})
        if not warning_data:
            return False

        try:
            warnings_list = warning_data.get("warnings", [])
            if not warnings_list:
                return False

            # Map sensor types to warning classifications
            classification_map = {
                "storm_warning": "storm",
                "flood_warning": "flood",
                "fire_warning": "fire",
                "heat_warning": "heat",
                "wind_warning": "strong-wind",
                "severe_weather_warning": "storm",
                "strong_wind_warning": "strong-wind",
                "thunderstorm_warning": "storm",
                "frost_warning": "frost",
                "rain_warning": "cold-rain",
                "snow_warning": "snow",
                "hail_warning": "storm",
                "cyclone_warning": "hurricane",
                "tsunami_warning": "tsunami",
                "fog_warning": "fog",
            }
            target_classification = classification_map.get(self._sensor_type)
            if not target_classification:
                return False

            # Check if any active warning matches this classification
            for warning in warnings_list:
                warning_type = warning.get("warningType", {})
                if warning_type.get("classification") == target_classification:
                    # Check expiry
                    expire_time_str = warning.get("expireDateTime")
                    if expire_time_str:
                        try:
                            expire_time = dt_util.parse_datetime(expire_time_str)
                            if expire_time and expire_time > dt_util.utcnow():
                                return True
                        except (ValueError, TypeError):
                            pass

            return False

        except (KeyError, TypeError) as err:
            _LOGGER.debug("Error getting warning value for %s: %s", self._sensor_type, err)
            return None