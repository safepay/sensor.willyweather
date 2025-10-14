"""Support for WillyWeather sensors."""
from __future__ import annotations

from datetime import datetime
import logging
from typing import TYPE_CHECKING, Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.util import dt as dt_util

from .const import (
    ATTRIBUTION,
    CONF_INCLUDE_OBSERVATIONAL,
    CONF_INCLUDE_UV,
    CONF_INCLUDE_TIDES,
    CONF_INCLUDE_WIND,
    CONF_STATION_ID,
    CONF_STATION_NAME,
    DOMAIN,
    MANUFACTURER,
    SENSOR_TYPES,
    SUNMOON_SENSOR_TYPES,
    TIDES_SENSOR_TYPES,
    UV_SENSOR_TYPES,
    WIND_FORECAST_TYPES,
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
    """Set up WillyWeather sensor based on a config entry."""
    coordinator: WillyWeatherDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []
    
    station_id = entry.data[CONF_STATION_ID]
    station_name = entry.data.get(CONF_STATION_NAME, f"Station {station_id}")

    # Add observational sensors if enabled
    if entry.options.get(CONF_INCLUDE_OBSERVATIONAL, True):
        for sensor_type in SENSOR_TYPES:
            entities.append(
                WillyWeatherSensor(
                    coordinator,
                    station_id,
                    station_name,
                    sensor_type,
                    SENSOR_TYPES,
                )
            )

        # Add sun/moon sensors
        for sensor_type in SUNMOON_SENSOR_TYPES:
            entities.append(
                WillyWeatherSunMoonSensor(
                    coordinator,
                    station_id,
                    station_name,
                    sensor_type,
                )
            )

    # Add tide sensors if enabled
    if entry.options.get(CONF_INCLUDE_TIDES, False):
        for sensor_type in TIDES_SENSOR_TYPES:
            entities.append(
                WillyWeatherTideSensor(
                    coordinator,
                    station_id,
                    station_name,
                    sensor_type,
                )
            )

    # Add UV sensors if enabled
    if entry.options.get(CONF_INCLUDE_UV, False):
        for sensor_type in UV_SENSOR_TYPES:
            entities.append(
                WillyWeatherUVSensor(
                    coordinator,
                    station_id,
                    station_name,
                    sensor_type,
                )
            )

    # Add wind forecast sensors if enabled
    if entry.options.get(CONF_INCLUDE_WIND, False):
        for sensor_type in WIND_FORECAST_TYPES:
            entities.append(
                WillyWeatherWindForecastSensor(
                    coordinator,
                    station_id,
                    station_name,
                    sensor_type,
                )
            )

    async_add_entities(entities)


class WillyWeatherSensor(CoordinatorEntity, SensorEntity):
    """Implementation of a WillyWeather observational sensor."""

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: WillyWeatherDataUpdateCoordinator,
        station_id: str,
        station_name: str,
        sensor_type: str,
        sensor_types_dict: dict,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._sensor_type = sensor_type
        self._sensor_types_dict = sensor_types_dict
        self._station_id = station_id
        self._station_name = station_name

        sensor_info = sensor_types_dict[sensor_type]
        self._attr_name = sensor_info["name"]
        self._attr_unique_id = f"{station_id}_{sensor_type}"
        self._attr_native_unit_of_measurement = sensor_info["unit"]
        self._attr_icon = sensor_info["icon"]
        self._attr_device_class = sensor_info.get("device_class")
        self._attr_state_class = sensor_info.get("state_class")

        self._attr_device_info = DeviceInfo(
            entry_type=DeviceEntryType.SERVICE,
            identifiers={(DOMAIN, f"{station_id}_sensors")},
            manufacturer=MANUFACTURER,
            name=f"{station_name} Sensors",
            via_device=(DOMAIN, station_id),
        )

    @property
    def native_value(self) -> Any:
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return None

        observations = self.coordinator.data.get("observational", {}).get("observations", {})
        
        sensor_info = self._sensor_types_dict[self._sensor_type]
        path = sensor_info["path"]
        
        value = observations
        for key in path:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return None
                
        return value


class WillyWeatherSunMoonSensor(CoordinatorEntity, SensorEntity):
    """Implementation of a WillyWeather sun/moon sensor."""

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: WillyWeatherDataUpdateCoordinator,
        station_id: str,
        station_name: str,
        sensor_type: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._sensor_type = sensor_type
        self._station_id = station_id
        self._station_name = station_name

        sensor_info = SUNMOON_SENSOR_TYPES[sensor_type]
        self._attr_name = sensor_info["name"]
        self._attr_unique_id = f"{station_id}_{sensor_type}"
        self._attr_native_unit_of_measurement = sensor_info.get("unit")
        self._attr_icon = sensor_info["icon"]
        self._attr_device_class = sensor_info.get("device_class")

        self._attr_device_info = DeviceInfo(
            entry_type=DeviceEntryType.SERVICE,
            identifiers={(DOMAIN, f"{station_id}_sensors")},
            manufacturer=MANUFACTURER,
            name=f"{station_name} Sensors",
            via_device=(DOMAIN, station_id),
        )

    @property
    def native_value(self) -> Any:
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return None

        try:
            forecasts = self.coordinator.data.get("forecast", {}).get("forecasts", {})
            
            # Handle sunrise/sunset
            if self._sensor_type in ["sunrise", "sunset"]:
                sunrisesunset_data = forecasts.get("sunrisesunset", {})
                if not sunrisesunset_data:
                    _LOGGER.debug("No sunrisesunset data available")
                    return None
                    
                days = sunrisesunset_data.get("days", [])
                if days and days[0].get("entries"):
                    entry = days[0]["entries"][0]
                    if self._sensor_type == "sunrise":
                        time_val = entry.get("riseDateTime")
                    else:  # sunset
                        time_val = entry.get("setDateTime")
                    if time_val:
                        dt = dt_util.parse_datetime(time_val)
                        if dt and dt.tzinfo is None:
                            # Assume UTC and convert to local timezone
                            dt = dt.replace(tzinfo=dt_util.UTC)
                            tz = self.coordinator.hass.config.time_zone
                            if tz:
                                local_tz = dt_util.get_time_zone(tz)
                                if local_tz:
                                    dt = dt.astimezone(local_tz)
                        return dt
            
            # Handle moon phases
            elif self._sensor_type in ["moonrise", "moonset", "moon_phase"]:
                moonphases_data = forecasts.get("moonphases", {})
                if not moonphases_data:
                    _LOGGER.debug("No moonphases data available")
                    return None
                    
                days = moonphases_data.get("days", [])
                if days and days[0].get("entries"):
                    entry = days[0]["entries"][0]
                    if self._sensor_type == "moonrise":
                        time_val = entry.get("riseDateTime")
                    elif self._sensor_type == "moonset":
                        time_val = entry.get("setDateTime")
                    else:  # moon_phase
                        return entry.get("phase")
                    
                    if time_val:
                        dt = dt_util.parse_datetime(time_val)
                        if dt and dt.tzinfo is None:
                            dt = dt.replace(tzinfo=dt_util.UTC)
                            tz = self.coordinator.hass.config.time_zone
                            if tz:
                                local_tz = dt_util.get_time_zone(tz)
                                if local_tz:
                                    dt = dt.astimezone(local_tz)
                        return dt

        except (KeyError, IndexError, TypeError) as err:
            _LOGGER.debug("Error getting sun/moon value for %s: %s", self._sensor_type, err)
            return None

        return None


class WillyWeatherTideSensor(CoordinatorEntity, SensorEntity):
    """Implementation of a WillyWeather tide sensor."""

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: WillyWeatherDataUpdateCoordinator,
        station_id: str,
        station_name: str,
        sensor_type: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._sensor_type = sensor_type
        self._station_id = station_id
        self._station_name = station_name

        sensor_info = TIDES_SENSOR_TYPES[sensor_type]
        self._attr_name = sensor_info["name"]
        self._attr_unique_id = f"{station_id}_{sensor_type}"
        self._attr_native_unit_of_measurement = sensor_info.get("unit")
        self._attr_icon = sensor_info["icon"]
        self._attr_device_class = sensor_info.get("device_class")

        self._attr_device_info = DeviceInfo(
            entry_type=DeviceEntryType.SERVICE,
            identifiers={(DOMAIN, f"{station_id}_sensors")},
            manufacturer=MANUFACTURER,
            name=f"{station_name} Sensors",
            via_device=(DOMAIN, station_id),
        )

    @property
    def native_value(self) -> Any:
        """Return the state of the sensor."""
        if not self.coordinator.data:
            _LOGGER.debug("No coordinator data for tides")
            return None

        try:
            forecasts = self.coordinator.data.get("forecast", {})
            if not forecasts:
                _LOGGER.debug("No forecast data available")
                return None
                
            forecasts_dict = forecasts.get("forecasts", {})
            if not forecasts_dict:
                _LOGGER.debug("No forecasts dict available")
                return None
            
            tides_data = forecasts_dict.get("tides")
            
            _LOGGER.debug("Tides data structure: %s", 
                         type(tides_data) if tides_data else "None")
            
            if not tides_data:
                _LOGGER.debug("No tides data in forecasts")
                return None
            
            days = tides_data.get("days", [])
            _LOGGER.debug("Tides days count: %d", len(days))
            
            if not days:
                _LOGGER.debug("No days in tides data")
                return None
            
            day_data = days[0]
            _LOGGER.debug("First day tides data keys: %s", day_data.keys() if isinstance(day_data, dict) else type(day_data))
            
            entries = day_data.get("entries", [])
            _LOGGER.debug("Tides entries count: %d", len(entries))
            
            if not entries:
                _LOGGER.debug("No entries in first tides day")
                return None
            
            # Find next high or low tide
            if self._sensor_type == "next_high_tide":
                for entry in entries:
                    entry_type = entry.get("type")
                    _LOGGER.debug("Tide entry type: %s", entry_type)
                    if entry_type == "high":
                        tide_time = entry.get("dateTime")
                        _LOGGER.debug("Found high tide time: %s", tide_time)
                        if tide_time:
                            dt = dt_util.parse_datetime(tide_time)
                            if dt and dt.tzinfo is None:
                                dt = dt.replace(tzinfo=dt_util.UTC)
                                tz = self.coordinator.hass.config.time_zone
                                if tz:
                                    local_tz = dt_util.get_time_zone(tz)
                                    if local_tz:
                                        dt = dt.astimezone(local_tz)
                            _LOGGER.debug("Returning high tide: %s", dt)
                            return dt
                        break
                _LOGGER.debug("No high tide found in entries")
                
            elif self._sensor_type == "next_low_tide":
                for entry in entries:
                    if entry.get("type") == "low":
                        tide_time = entry.get("dateTime")
                        _LOGGER.debug("Found low tide time: %s", tide_time)
                        if tide_time:
                            dt = dt_util.parse_datetime(tide_time)
                            if dt and dt.tzinfo is None:
                                dt = dt.replace(tzinfo=dt_util.UTC)
                                tz = self.coordinator.hass.config.time_zone
                                if tz:
                                    local_tz = dt_util.get_time_zone(tz)
                                    if local_tz:
                                        dt = dt.astimezone(local_tz)
                            _LOGGER.debug("Returning low tide: %s", dt)
                            return dt
                        break
                _LOGGER.debug("No low tide found in entries")
                
            elif self._sensor_type == "next_high_tide_height":
                for entry in entries:
                    if entry.get("type") == "high":
                        height = entry.get("height")
                        _LOGGER.debug("High tide height: %s", height)
                        return height
                        
            elif self._sensor_type == "next_low_tide_height":
                for entry in entries:
                    if entry.get("type") == "low":
                        height = entry.get("height")
                        _LOGGER.debug("Low tide height: %s", height)
                        return height

        except (KeyError, IndexError, TypeError) as err:
            _LOGGER.error("Error getting tide value for %s: %s", self._sensor_type, err, exc_info=True)
            return None

        return None

class WillyWeatherUVSensor(CoordinatorEntity, SensorEntity):
    """Implementation of a WillyWeather UV sensor."""

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: WillyWeatherDataUpdateCoordinator,
        station_id: str,
        station_name: str,
        sensor_type: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._sensor_type = sensor_type
        self._station_id = station_id
        self._station_name = station_name

        sensor_info = UV_SENSOR_TYPES[sensor_type]
        self._attr_name = sensor_info["name"]
        self._attr_unique_id = f"{station_id}_{sensor_type}"
        self._attr_native_unit_of_measurement = sensor_info.get("unit")
        self._attr_icon = sensor_info["icon"]

        self._attr_device_info = DeviceInfo(
            entry_type=DeviceEntryType.SERVICE,
            identifiers={(DOMAIN, f"{station_id}_sensors")},
            manufacturer=MANUFACTURER,
            name=f"{station_name} Sensors",
            via_device=(DOMAIN, station_id),
        )

    @property
    def native_value(self) -> Any:
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return None

        try:
            forecasts = self.coordinator.data.get("forecast", {}).get("forecasts", {})
            uv_days = forecasts.get("uv", {}).get("days", [])
            
            if not uv_days or not uv_days[0].get("entries"):
                return None
            
            entry = uv_days[0]["entries"][0]
            
            if self._sensor_type == "uv_index":
                return entry.get("index")
            elif self._sensor_type == "uv_alert":
                uv_index = entry.get("index")
                if uv_index is None:
                    return None
                if uv_index >= 11:
                    return "Extreme"
                elif uv_index >= 8:
                    return "Very High"
                elif uv_index >= 6:
                    return "High"
                elif uv_index >= 3:
                    return "Moderate"
                else:
                    return "Low"

        except (KeyError, IndexError, TypeError) as err:
            _LOGGER.debug("Error getting UV value for %s: %s", self._sensor_type, err)
            return None

        return None


class WillyWeatherWindForecastSensor(CoordinatorEntity, SensorEntity):
    """Implementation of a WillyWeather wind forecast sensor."""

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: WillyWeatherDataUpdateCoordinator,
        station_id: str,
        station_name: str,
        sensor_type: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._sensor_type = sensor_type
        self._station_id = station_id
        self._station_name = station_name

        sensor_info = WIND_FORECAST_TYPES[sensor_type]
        self._attr_name = sensor_info["name"]
        self._attr_unique_id = f"{station_id}_{sensor_type}"
        self._attr_native_unit_of_measurement = sensor_info.get("unit")
        self._attr_icon = sensor_info["icon"]
        self._attr_device_class = sensor_info.get("device_class")

        self._attr_device_info = DeviceInfo(
            entry_type=DeviceEntryType.SERVICE,
            identifiers={(DOMAIN, f"{station_id}_sensors")},
            manufacturer=MANUFACTURER,
            name=f"{station_name} Sensors",
            via_device=(DOMAIN, station_id),
        )

    @property
    def native_value(self) -> Any:
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return None

        try:
            forecasts = self.coordinator.data.get("forecast", {}).get("forecasts", {})
            wind_days = forecasts.get("wind", {}).get("days", [])
            
            if not wind_days or not wind_days[0].get("entries"):
                return None
            
            entry = wind_days[0]["entries"][0]
            
            if self._sensor_type == "wind_speed_forecast":
                return entry.get("speed")
            elif self._sensor_type == "wind_direction_forecast":
                return entry.get("direction")

        except (KeyError, IndexError, TypeError) as err:
            _LOGGER.debug("Error getting wind forecast value for %s: %s", self._sensor_type, err)
            return None

        return None