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
            identifiers={(DOMAIN, station_id)},
            manufacturer=MANUFACTURER,
            name=station_name,
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
            identifiers={(DOMAIN, station_id)},
            manufacturer=MANUFACTURER,
            name=station_name,
        )

    @property
    def native_value(self) -> Any:
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return None

        try:
            forecasts = self.coordinator.data.get("forecast", {}).get("forecasts", {})
            sunrisesunset_data = forecasts.get("sunrisesunset", {})
            days = sunrisesunset_data.get("days", [])
            
            if not days or not days[0].get("entries"):
                return None
            
            entry = days[0]["entries"][0]
            
            if self._sensor_type == "sunrise":
                sunrise_time = entry.get("firstLightDateTime")
                if sunrise_time:
                    return dt_util.parse_datetime(sunrise_time)
            elif self._sensor_type == "sunset":
                sunset_time = entry.get("lastLightDateTime")
                if sunset_time:
                    return dt_util.parse_datetime(sunset_time)
            elif self._sensor_type == "moonrise":
                moonrise_time = entry.get("moonrise")
                if moonrise_time:
                    return dt_util.parse_datetime(moonrise_time)
            elif self._sensor_type == "moonset":
                moonset_time = entry.get("moonset")
                if moonset_time:
                    return dt_util.parse_datetime(moonset_time)
            elif self._sensor_type == "moon_phase":
                return entry.get("moonPhaseDescription")

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
            identifiers={(DOMAIN, station_id)},
            manufacturer=MANUFACTURER,
            name=station_name,
        )

    @property
    def native_value(self) -> Any:
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return None

        try:
            forecasts = self.coordinator.data.get("forecast", {}).get("forecasts", {})
            tides_data = forecasts.get("tides", {})
            days = tides_data.get("days", [])
            
            if not days or not days[0].get("entries"):
                return None
            
            entries = days[0]["entries"]
            
            if self._sensor_type == "next_high_tide":
                for entry in entries:
                    if entry.get("type") == "high":
                        tide_time = entry.get("dateTime")
                        if tide_time:
                            return dt_util.parse_datetime(tide_time)
                        break
            elif self._sensor_type == "next_low_tide":
                for entry in entries:
                    if entry.get("type") == "low":
                        tide_time = entry.get("dateTime")
                        if tide_time:
                            return dt_util.parse_datetime(tide_time)
                        break
            elif self._sensor_type == "next_high_tide_height":
                for entry in entries:
                    if entry.get("type") == "high":
                        return entry.get("height")
            elif self._sensor_type == "next_low_tide_height":
                for entry in entries:
                    if entry.get("type") == "low":
                        return entry.get("height")

        except (KeyError, IndexError, TypeError) as err:
            _LOGGER.debug("Error getting tide value for %s: %s", self._sensor_type, err)
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
            identifiers={(DOMAIN, station_id)},
            manufacturer=MANUFACTURER,
            name=station_name,
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
            identifiers={(DOMAIN, station_id)},
            manufacturer=MANUFACTURER,
            name=station_name,
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