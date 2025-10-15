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
                "weather_warning": "storm",  # Changed from severe_weather_warning
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
                            if expire_time:
                                # Handle timezone
                                if expire_time.tzinfo is None:
                                    tz = dt_util.get_time_zone(self.coordinator.hass.config.time_zone)
                                    if tz:
                                        try:
                                            expire_time = tz.localize(expire_time)
                                        except AttributeError:
                                            expire_time = expire_time.replace(tzinfo=tz)
                                
                                if expire_time > dt_util.now():
                                    return True
                        except (ValueError, TypeError):
                            pass

            return False

        except (KeyError, TypeError) as err:
            _LOGGER.debug("Error getting warning value for %s: %s", self._sensor_type, err)
            return None
    
    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional state attributes."""
        if not self.coordinator.data:
            _LOGGER.debug("No coordinator data for %s", self._sensor_type)
            return {}

        warning_data = self.coordinator.data.get("warnings", {})
        _LOGGER.debug("Warning data for %s: %s", self._sensor_type, warning_data)
        
        if not warning_data:
            _LOGGER.debug("No warning data dict for %s", self._sensor_type)
            return {}

        try:
            warnings_list = warning_data.get("warnings", [])
            _LOGGER.debug("Warnings list for %s: %s warnings found", self._sensor_type, len(warnings_list))
            
            if not warnings_list:
                return {}

            # Map sensor types to warning classifications
            classification_map = {
                "storm_warning": "storm",
                "flood_warning": "flood",
                "fire_warning": "fire",
                "heat_warning": "heat",
                "wind_warning": "strong-wind",
                "weather_warning": "storm",  # Changed from severe_weather_warning
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
            _LOGGER.debug("Looking for classification: %s for sensor %s", target_classification, self._sensor_type)
            
            if not target_classification:
                return {}

            # Collect all active warnings for this classification
            active_warnings = []
            for warning in warnings_list:
                warning_type = warning.get("warningType", {})
                warning_classification = warning_type.get("classification")
                _LOGGER.debug("Checking warning with classification: %s", warning_classification)
                
                if warning_classification == target_classification:
                    # Check expiry
                    expire_time_str = warning.get("expireDateTime")
                    if expire_time_str:
                        try:
                            expire_time = dt_util.parse_datetime(expire_time_str)
                            if expire_time:
                                # Handle timezone
                                if expire_time.tzinfo is None:
                                    tz = dt_util.get_time_zone(self.coordinator.hass.config.time_zone)
                                    if tz:
                                        try:
                                            expire_time = tz.localize(expire_time)
                                        except AttributeError:
                                            expire_time = expire_time.replace(tzinfo=tz)
                                
                                now = dt_util.now()
                                _LOGGER.debug("Warning expires at %s, now is %s, active: %s", 
                                            expire_time, now, expire_time > now)
                                
                                if expire_time > now:
                                    # Get severity levels
                                    severity_levels = warning_type.get("warningSeverityLevels", [])
                                    severity = None
                                    if severity_levels:
                                        # Get the highest severity level (red is highest)
                                        # Find red first, then amber, then yellow
                                        for level in severity_levels:
                                            level_code = level.get("code")
                                            if level_code == "red":
                                                severity = "red"
                                                break
                                            elif level_code == "amber" and severity != "red":
                                                severity = "amber"
                                            elif level_code == "yellow" and not severity:
                                                severity = "yellow"
                                    
                                    _LOGGER.debug("Adding active warning with severity: %s", severity)
                                    
                                    active_warnings.append({
                                        "code": warning.get("code"),
                                        "name": warning.get("name"),
                                        "issue_time": warning.get("issueDateTime"),
                                        "expire_time": expire_time_str,
                                        "severity": severity,
                                        "warning_type": warning_type.get("name"),
                                    })
                        except (ValueError, TypeError) as err:
                            _LOGGER.debug("Error parsing warning time: %s", err)
                            pass

            _LOGGER.debug("Found %s active warnings for %s", len(active_warnings), self._sensor_type)

            if not active_warnings:
                return {}

            # If multiple warnings, return the highest severity (red > amber > yellow)
            severity_order = {"yellow": 1, "amber": 2, "red": 3}
            highest_severity = "yellow"
            
            for warn in active_warnings:
                warn_severity = warn.get("severity")
                if warn_severity:
                    if severity_order.get(warn_severity, 0) > severity_order.get(highest_severity, 0):
                        highest_severity = warn_severity

            attributes = {
                "severity": highest_severity,
                "warning_count": len(active_warnings),
                "warnings": active_warnings,
            }
            
            _LOGGER.debug("Returning attributes for %s: %s", self._sensor_type, attributes)
            return attributes

        except (KeyError, TypeError) as err:
            _LOGGER.error("Error getting warning attributes for %s: %s", self._sensor_type, err, exc_info=True)
            return {}