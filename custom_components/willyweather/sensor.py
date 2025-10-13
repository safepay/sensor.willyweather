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
    BOM_FORECAST_TYPES,
    BOM_RAINFALL_TYPES,
    BOM_UV_TYPES,
    CONDITION_MAP,
    CONF_FORECAST_DAYS,
    CONF_FORECAST_RAINFALL,
    CONF_FORECAST_SUNRISESUNSET,
    CONF_FORECAST_TIDES,
    CONF_FORECAST_UV,
    CONF_SENSOR_FORMAT,
    CONF_STATION_ID,
    CONF_STATION_NAME,
    DARKSKY_FORECAST_TYPES,
    DARKSKY_RAINFALL_TYPES,
    DARKSKY_UV_TYPES,
    DEFAULT_FORECAST_DAYS,
    DOMAIN,
    MANUFACTURER,
    SENSOR_FORMAT_BOM,
    SENSOR_FORMAT_DARKSKY,
    SENSOR_TYPES,
    SUNMOON_SENSOR_TYPES,
    TIDES_SENSOR_TYPES,
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
    sensor_format = entry.options.get(CONF_SENSOR_FORMAT, SENSOR_FORMAT_DARKSKY)
    forecast_days = entry.options.get(CONF_FORECAST_DAYS, DEFAULT_FORECAST_DAYS)

    # Always add observational sensors
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

    # Add forecast sensors based on format
    if sensor_format == SENSOR_FORMAT_DARKSKY:
        # Dark Sky format forecast sensors
        for day in range(forecast_days):
            for sensor_type in DARKSKY_FORECAST_TYPES:
                entities.append(
                    WillyWeatherDarkSkyForecastSensor(
                        coordinator,
                        station_id,
                        station_name,
                        sensor_type,
                        day,
                    )
                )
            
            # Add rainfall sensors if enabled
            if entry.options.get(CONF_FORECAST_RAINFALL, False):
                for sensor_type in DARKSKY_RAINFALL_TYPES:
                    entities.append(
                        WillyWeatherDarkSkyForecastSensor(
                            coordinator,
                            station_id,
                            station_name,
                            sensor_type,
                            day,
                        )
                    )
            
            # Add UV sensors if enabled
            if entry.options.get(CONF_FORECAST_UV, False):
                for sensor_type in DARKSKY_UV_TYPES:
                    entities.append(
                        WillyWeatherDarkSkyForecastSensor(
                            coordinator,
                            station_id,
                            station_name,
                            sensor_type,
                            day,
                        )
                    )
    
    elif sensor_format == SENSOR_FORMAT_BOM:
        # BoM format forecast sensors
        for day in range(forecast_days):
            for sensor_type in BOM_FORECAST_TYPES:
                entities.append(
                    WillyWeatherBomForecastSensor(
                        coordinator,
                        station_id,
                        station_name,
                        sensor_type,
                        day,
                    )
                )
            
            # Add rainfall sensors if enabled
            if entry.options.get(CONF_FORECAST_RAINFALL, False):
                for sensor_type in BOM_RAINFALL_TYPES:
                    entities.append(
                        WillyWeatherBomForecastSensor(
                            coordinator,
                            station_id,
                            station_name,
                            sensor_type,
                            day,
                        )
                    )
            
            # Add UV sensors if enabled
            if entry.options.get(CONF_FORECAST_UV, False):
                for sensor_type in BOM_UV_TYPES:
                    entities.append(
                        WillyWeatherBomForecastSensor(
                            coordinator,
                            station_id,
                            station_name,
                            sensor_type,
                            day,
                        )
                    )

    # Add sun/moon sensors if enabled (format independent)
    if entry.options.get(CONF_FORECAST_SUNRISESUNSET, False):
        for sensor_type in SUNMOON_SENSOR_TYPES:
            entities.append(
                WillyWeatherSunMoonSensor(
                    coordinator,
                    station_id,
                    station_name,
                    sensor_type,
                )
            )

    # Add tide sensors if enabled (format independent)
    if entry.options.get(CONF_FORECAST_TIDES, False):
        for sensor_type in TIDES_SENSOR_TYPES:
            entities.append(
                WillyWeatherTideSensor(
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
        
        # Navigate the path to get the value
        sensor_info = self._sensor_types_dict[self._sensor_type]
        path = sensor_info["path"]
        
        value = observations
        for key in path:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return None
                
        return value


class WillyWeatherDarkSkyForecastSensor(CoordinatorEntity, SensorEntity):
    """Implementation of a WillyWeather Dark Sky format forecast sensor."""

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: WillyWeatherDataUpdateCoordinator,
        station_id: str,
        station_name: str,
        sensor_type: str,
        day: int,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._sensor_type = sensor_type
        self._station_id = station_id
        self._station_name = station_name
        self._day = day

        # Determine which sensor type dict to use
        if sensor_type in DARKSKY_FORECAST_TYPES:
            sensor_info = DARKSKY_FORECAST_TYPES[sensor_type]
        elif sensor_type in DARKSKY_RAINFALL_TYPES:
            sensor_info = DARKSKY_RAINFALL_TYPES[sensor_type]
        elif sensor_type in DARKSKY_UV_TYPES:
            sensor_info = DARKSKY_UV_TYPES[sensor_type]
        else:
            raise ValueError(f"Unknown sensor type: {sensor_type}")

        # Dark Sky format: "Sensor Name d" where d is day number
        self._attr_name = f"{sensor_info['name']} {day}"
        self._attr_unique_id = f"{station_id}_{sensor_type}_{day}"
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
            
            # Get weather forecast data
            if self._sensor_type in ["forecast_icon", "forecast_summary", "forecast_temp_high", "forecast_temp_low"]:
                weather_days = forecasts.get("weather", {}).get("days", [])
                if self._day >= len(weather_days):
                    return None
                
                day_data = weather_days[self._day]
                if not day_data.get("entries"):
                    return None
                
                entry = day_data["entries"][0]
                
                if self._sensor_type == "forecast_icon":
                    precis_code = entry.get("precisCode")
                    return CONDITION_MAP.get(precis_code, "unknown")
                elif self._sensor_type == "forecast_summary":
                    return entry.get("precis")
                elif self._sensor_type == "forecast_temp_high":
                    return entry.get("max")
                elif self._sensor_type == "forecast_temp_low":
                    return entry.get("min")
            
            # Get rainfall data
            elif self._sensor_type in ["forecast_precip", "forecast_precip_probability"]:
                rainfall_days = forecasts.get("rainfall", {}).get("days", [])
                if self._day >= len(rainfall_days):
                    return None
                
                day_data = rainfall_days[self._day]
                if not day_data.get("entries"):
                    return None
                
                entry = day_data["entries"][0]
                
                if self._sensor_type == "forecast_precip":
                    # Use average of range
                    start_range = entry.get("startRange")
                    end_range = entry.get("endRange")
                    if start_range is not None and end_range is not None:
                        return (start_range + end_range) / 2
                    elif end_range is not None:
                        return end_range
                    return None
                elif self._sensor_type == "forecast_precip_probability":
                    return entry.get("probability")
            
            # Get UV data
            elif self._sensor_type == "forecast_uv_index":
                uv_days = forecasts.get("uv", {}).get("days", [])
                if self._day >= len(uv_days):
                    return None
                
                day_data = uv_days[self._day]
                if not day_data.get("entries"):
                    return None
                
                entry = day_data["entries"][0]
                return entry.get("index")

        except (KeyError, IndexError, TypeError) as err:
            _LOGGER.debug("Error getting forecast value for %s day %s: %s", self._sensor_type, self._day, err)
            return None

        return None


class WillyWeatherBomForecastSensor(CoordinatorEntity, SensorEntity):
    """Implementation of a WillyWeather BoM format forecast sensor."""

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: WillyWeatherDataUpdateCoordinator,
        station_id: str,
        station_name: str,
        sensor_type: str,
        day: int,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._sensor_type = sensor_type
        self._station_id = station_id
        self._station_name = station_name
        self._day = day

        # Determine which sensor type dict to use
        if sensor_type in BOM_FORECAST_TYPES:
            sensor_info = BOM_FORECAST_TYPES[sensor_type]
        elif sensor_type in BOM_RAINFALL_TYPES:
            sensor_info = BOM_RAINFALL_TYPES[sensor_type]
        elif sensor_type in BOM_UV_TYPES:
            sensor_info = BOM_UV_TYPES[sensor_type]
        else:
            raise ValueError(f"Unknown sensor type: {sensor_type}")

        # BoM format: "location_sensor_name_day" (lowercase with underscores)
        location_slug = station_name.lower().replace(" ", "_").replace("-", "_")
        sensor_slug = sensor_info['name'].lower().replace(" ", "_")
        
        self._attr_name = f"{sensor_info['name']} {day}"
        self._attr_unique_id = f"{station_id}_{sensor_type}_{day}"
        # Set entity_id format for BoM compatibility
        self.entity_id = f"sensor.{location_slug}_{sensor_slug}_{day}"
        
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
            
            # Get weather forecast data
            if self._sensor_type in ["icon_descriptor", "short_text", "temp_max", "temp_min"]:
                weather_days = forecasts.get("weather", {}).get("days", [])
                if self._day >= len(weather_days):
                    return None
                
                day_data = weather_days[self._day]
                if not day_data.get("entries"):
                    return None
                
                entry = day_data["entries"][0]
                
                if self._sensor_type == "icon_descriptor":
                    precis_code = entry.get("precisCode")
                    return precis_code
                elif self._sensor_type == "short_text":
                    return entry.get("precis")
                elif self._sensor_type == "temp_max":
                    return entry.get("max")
                elif self._sensor_type == "temp_min":
                    return entry.get("min")
            
            # Get rainfall data
            elif self._sensor_type in ["rain_amount_min", "rain_amount_max", "rain_amount_range", "rain_chance"]:
                rainfall_days = forecasts.get("rainfall", {}).get("days", [])
                if self._day >= len(rainfall_days):
                    return None
                
                day_data = rainfall_days[self._day]
                if not day_data.get("entries"):
                    return None
                
                entry = day_data["entries"][0]
                
                if self._sensor_type == "rain_amount_min":
                    return entry.get("startRange")
                elif self._sensor_type == "rain_amount_max":
                    return entry.get("endRange")
                elif self._sensor_type == "rain_amount_range":
                    # Return formatted range string
                    start = entry.get("startRange")
                    end = entry.get("endRange")
                    if start is not None and end is not None:
                        return f"{start}-{end}"
                    elif end is not None:
                        return str(end)
                    return None
                elif self._sensor_type == "rain_chance":
                    return entry.get("probability")
            
            # Get UV data
            elif self._sensor_type in ["uv_alert", "uv_category", "uv_max_index"]:
                uv_days = forecasts.get("uv", {}).get("days", [])
                if self._day >= len(uv_days):
                    return None
                
                day_data = uv_days[self._day]
                if not day_data.get("entries"):
                    return None
                
                entry = day_data["entries"][0]
                
                if self._sensor_type == "uv_alert":
                    # Create UV alert based on index
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
                elif self._sensor_type == "uv_category":
                    # Similar to alert but different terminology
                    uv_index = entry.get("index")
                    if uv_index is None:
                        return None
                    if uv_index >= 11:
                        return "extreme"
                    elif uv_index >= 8:
                        return "veryhigh"
                    elif uv_index >= 6:
                        return "high"
                    elif uv_index >= 3:
                        return "moderate"
                    else:
                        return "low"
                elif self._sensor_type == "uv_max_index":
                    return entry.get("index")

        except (KeyError, IndexError, TypeError) as err:
            _LOGGER.debug("Error getting forecast value for %s day %s: %s", self._sensor_type, self._day, err)
            return None

        return None

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
            
            # Find next high or low tide
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