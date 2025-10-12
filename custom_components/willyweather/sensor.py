"""Support for the WillyWeather Australia service."""
import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    ATTRIBUTION,
    CONF_API_KEY,
    CONF_DAYS,
    CONF_STATION_ID,
    DOMAIN,
    FORECAST_TYPES,
    SENSOR_TYPES,
)
from .coordinator import WillyWeatherDataCoordinator, WillyWeatherForecastCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up WillyWeather sensor based on a config entry."""
    api_key = entry.data[CONF_API_KEY]
    station_id = entry.data[CONF_STATION_ID]
    days = entry.data.get(CONF_DAYS)

    # Create observational coordinator
    obs_coordinator = WillyWeatherDataCoordinator(hass, api_key, station_id)
    await obs_coordinator.async_config_entry_first_refresh()

    entities = []

    # Add observational sensors
    for sensor_type in SENSOR_TYPES:
        entities.append(WWWeatherSensor(obs_coordinator, sensor_type, station_id))

    # Add forecast sensors if days configured
    if days:
        forecast_coordinator = WillyWeatherForecastCoordinator(
            hass, api_key, station_id, days
        )
        await forecast_coordinator.async_config_entry_first_refresh()

        if forecast_coordinator.data and "forecasts" in forecast_coordinator.data:
            forecast_days = forecast_coordinator.data.get("forecasts", {}).get(
                "weather", {}
            ).get("days", [])
            for day_num in range(len(forecast_days)):
                for forecast_type in FORECAST_TYPES:
                    entities.append(
                        WWForecastSensor(
                            forecast_coordinator, forecast_type, station_id, day_num
                        )
                    )

    async_add_entities(entities)


class WWWeatherSensor(CoordinatorEntity, SensorEntity):
    """Implementation of a WillyWeather sensor."""

    _attr_attribution = ATTRIBUTION

    def __init__(
        self,
        coordinator: WillyWeatherDataCoordinator,
        sensor_type: str,
        station_id: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._sensor_type = sensor_type
        self._station_id = station_id

        sensor_info = SENSOR_TYPES[sensor_type]
        self._attr_name = f"WillyWeather {sensor_info['name']}"
        self._attr_unique_id = f"{station_id}_{sensor_type}"
        self._attr_native_unit_of_measurement = sensor_info['unit']
        self._attr_icon = sensor_info['icon']
        self._attr_device_class = sensor_info['device_class']
        self._attr_state_class = sensor_info['state_class']

    @property
    def native_value(self) -> Any:
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return None

        observations = self.coordinator.data.get("observations", {})

        value_map = {
            'temperature': lambda: observations.get("temperature", {}).get("temperature"),
            'apparent_temperature': lambda: observations.get("temperature", {}).get("apparentTemperature"),
            'cloud': lambda: observations.get("cloud", {}).get("oktas"),
            'humidity': lambda: observations.get("humidity", {}).get("percentage"),
            'dewpoint': lambda: observations.get("dewPoint", {}).get("temperature"),
            'pressure': lambda: observations.get("pressure", {}).get("pressure"),
            'wind_speed': lambda: observations.get("wind", {}).get("speed"),
            'wind_gust': lambda: observations.get("wind", {}).get("gustSpeed"),
            'wind_bearing': lambda: observations.get("wind", {}).get("direction"),
            'wind_direction': lambda: observations.get("wind", {}).get("directionText"),
            'rainlasthour': lambda: observations.get("rainfall", {}).get("lastHourAmount"),
            'raintoday': lambda: observations.get("rainfall", {}).get("todayAmount"),
            'rainsince9am': lambda: observations.get("rainfall", {}).get("since9AMAmount"),
        }

        if self._sensor_type in value_map:
            return value_map[self._sensor_type]()

        return None


class WWForecastSensor(CoordinatorEntity, SensorEntity):
    """Implementation of a WillyWeather forecast sensor."""

    _attr_attribution = ATTRIBUTION

    def __init__(
        self,
        coordinator: WillyWeatherForecastCoordinator,
        forecast_type: str,
        station_id: str,
        day: int,
    ) -> None:
        """Initialize the forecast sensor."""
        super().__init__(coordinator)
        self._forecast_type = forecast_type
        self._station_id = station_id
        self._day = day

        forecast_info = FORECAST_TYPES[forecast_type]
        self._attr_name = f"WillyWeather Day {day} {forecast_info['name']}"
        self._attr_unique_id = f"{station_id}_day_{day}_{forecast_type}"
        self._attr_native_unit_of_measurement = forecast_info['unit']
        self._attr_icon = forecast_info['icon']

    @property
    def native_value(self) -> Any:
        """Return the state of the sensor."""
        if not self.coordinator.data:
            return None

        try:
            forecasts = self.coordinator.data.get("forecasts", {})
            weather_days = forecasts.get("weather", {}).get("days", [])
            rainfall_days = forecasts.get("rainfall", {}).get("days", [])

            if self._day >= len(weather_days):
                return None

            weather_entry = weather_days[self._day].get("entries", [{}])[0]

            if self._forecast_type == 'forecast_maxtemp':
                return weather_entry.get("max")
            elif self._forecast_type == 'forecast_mintemp':
                return weather_entry.get("min")
            elif self._forecast_type == 'forecast_summary':
                return weather_entry.get("precis")
            elif self._forecast_type == 'forecast_icon':
                from .const import DARK_SKY_ICONS
                precis_code = weather_entry.get("precisCode")
                return DARK_SKY_ICONS.get(precis_code) if precis_code else None
            elif self._forecast_type == 'forecast_rain':
                if self._day < len(rainfall_days):
                    rainfall_entry = rainfall_days[self._day].get("entries", [{}])[0]
                    return rainfall_entry.get("endRange")
            elif self._forecast_type == 'forecast_rain_prob':
                if self._day < len(rainfall_days):
                    rainfall_entry = rainfall_days[self._day].get("entries", [{}])[0]
                    return rainfall_entry.get("probability")

        except (KeyError, IndexError, TypeError) as err:
            _LOGGER.debug("Error getting forecast value: %s", err)
            return None

        return None
