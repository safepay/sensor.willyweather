"""Support for the WillyWeather Australia weather service."""
import logging
from datetime import datetime
from typing import Any

from homeassistant.components.weather import (
    ATTR_FORECAST_CONDITION,
    ATTR_FORECAST_NATIVE_PRECIPITATION,
    ATTR_FORECAST_NATIVE_TEMP,
    ATTR_FORECAST_NATIVE_TEMP_LOW,
    ATTR_FORECAST_PRECIPITATION_PROBABILITY,
    ATTR_FORECAST_TIME,
    Forecast,
    WeatherEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    ATTRIBUTION,
    CONF_API_KEY,
    CONF_DAYS,
    CONF_STATION_ID,
    DEFAULT_DAYS,
    DOMAIN,
    MAP_CONDITION,
)
from .coordinator import WillyWeatherForecastCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up WillyWeather weather based on a config entry."""
    api_key = entry.data[CONF_API_KEY]
    station_id = entry.data[CONF_STATION_ID]
    days = entry.data.get(CONF_DAYS, DEFAULT_DAYS)

    coordinator = WillyWeatherForecastCoordinator(hass, api_key, station_id, days)
    await coordinator.async_config_entry_first_refresh()

    async_add_entities([WWWeatherForecast(coordinator, station_id)])


class WWWeatherForecast(CoordinatorEntity, WeatherEntity):
    """Implementation of the WillyWeather weather component."""

    _attr_attribution = ATTRIBUTION
    _attr_native_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_native_pressure_unit = "hPa"
    _attr_native_wind_speed_unit = "km/h"
    _attr_native_precipitation_unit = "mm"

    def __init__(
        self,
        coordinator: WillyWeatherForecastCoordinator,
        station_id: str,
    ) -> None:
        """Initialize the component."""
        super().__init__(coordinator)
        self._station_id = station_id
        self._attr_unique_id = f"{station_id}_weather"

    @property
    def name(self) -> str:
        """Return the name."""
        if self.coordinator.data:
            location_name = self.coordinator.data.get("location", {}).get("name")
            if location_name:
                return f"WillyWeather {location_name}"
        return f"WillyWeather {self._station_id}"

    @property
    def condition(self) -> str | None:
        """Return the weather condition."""
        if not self.coordinator.data:
            return None

        try:
            forecasts = self.coordinator.data.get("forecasts", {})
            weather_days = forecasts.get("weather", {}).get("days", [])
            if weather_days:
                precis_code = weather_days[0].get("entries", [{}])[0].get("precisCode")
                return MAP_CONDITION.get(precis_code)
        except (KeyError, IndexError, TypeError):
            return None

        return None

    @property
    def native_temperature(self) -> float | None:
        """Return the temperature."""
        if not self.coordinator.data:
            return None

        try:
            observational = self.coordinator.data.get("observational", {})
            return observational.get("observations", {}).get("temperature", {}).get("temperature")
        except (KeyError, TypeError):
            return None

    @property
    def native_pressure(self) -> float | None:
        """Return the pressure."""
        if not self.coordinator.data:
            return None

        try:
            observational = self.coordinator.data.get("observational", {})
            return observational.get("observations", {}).get("pressure", {}).get("pressure")
        except (KeyError, TypeError):
            return None

    @property
    def humidity(self) -> float | None:
        """Return the humidity."""
        if not self.coordinator.data:
            return None

        try:
            observational = self.coordinator.data.get("observational", {})
            return observational.get("observations", {}).get("humidity", {}).get("percentage")
        except (KeyError, TypeError):
            return None

    @property
    def native_wind_speed(self) -> float | None:
        """Return the wind speed."""
        if not self.coordinator.data:
            return None

        try:
            observational = self.coordinator.data.get("observational", {})
            return observational.get("observations", {}).get("wind", {}).get("speed")
        except (KeyError, TypeError):
            return None

    @property
    def wind_bearing(self) -> float | None:
        """Return the wind direction."""
        if not self.coordinator.data:
            return None

        try:
            observational = self.coordinator.data.get("observational", {})
            return observational.get("observations", {}).get("wind", {}).get("direction")
        except (KeyError, TypeError):
            return None

    @property
    def forecast(self) -> list[Forecast] | None:
        """Return the forecast array."""
        if not self.coordinator.data:
            return None

        try:
            forecasts = self.coordinator.data.get("forecasts", {})
            weather_days = forecasts.get("weather", {}).get("days", [])
            rainfall_days = forecasts.get("rainfall", {}).get("days", [])

            forecast_data = []
            for num, day in enumerate(weather_days):
                if not day.get("entries"):
                    continue

                entry = day["entries"][0]
                date_string = entry.get("dateTime")
                
                if date_string:
                    # Parse and format the datetime
                    dt = datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
                    formatted_time = dt.isoformat()
                else:
                    continue

                # Get rainfall data if available
                rain_amount = None
                rain_prob = None
                if num < len(rainfall_days) and rainfall_days[num].get("entries"):
                    rain_entry = rainfall_days[num]["entries"][0]
                    rain_amount = rain_entry.get("endRange")
                    rain_prob = rain_entry.get("probability")

                forecast_dict: Forecast = {
                    ATTR_FORECAST_TIME: formatted_time,
                    ATTR_FORECAST_NATIVE_TEMP: entry.get("max"),
                    ATTR_FORECAST_NATIVE_TEMP_LOW: entry.get("min"),
                    ATTR_FORECAST_CONDITION: MAP_CONDITION.get(entry.get("precisCode")),
                }

                if rain_amount is not None:
                    forecast_dict[ATTR_FORECAST_NATIVE_PRECIPITATION] = rain_amount
                if rain_prob is not None:
                    forecast_dict[ATTR_FORECAST_PRECIPITATION_PROBABILITY] = rain_prob

                forecast_data.append(forecast_dict)

            return forecast_data if forecast_data else None

        except (KeyError, IndexError, TypeError, ValueError) as err:
            _LOGGER.error("Error parsing forecast data: %s", err)
            return None
