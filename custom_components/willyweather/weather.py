"""Support for WillyWeather weather entity."""
from __future__ import annotations

from datetime import datetime
import logging
from typing import TYPE_CHECKING, Any

from homeassistant.components.weather import (
    Forecast,
    SingleCoordinatorWeatherEntity,
    WeatherEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    UnitOfPrecipitationDepth,
    UnitOfPressure,
    UnitOfSpeed,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceEntryType, DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    ATTRIBUTION,
    CONDITION_MAP,
    CONF_FORECAST_RAINFALL,
    CONF_FORECAST_UV,
    CONF_STATION_ID,
    CONF_STATION_NAME,
    DOMAIN,
    MANUFACTURER,
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
    """Set up WillyWeather weather entity based on a config entry."""
    coordinator: WillyWeatherDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities([WillyWeatherEntity(coordinator, entry)])


class WillyWeatherEntity(SingleCoordinatorWeatherEntity):
    """Implementation of a WillyWeather weather entity."""

    _attr_attribution = ATTRIBUTION
    _attr_has_entity_name = True
    _attr_name = None
    _attr_native_precipitation_unit = UnitOfPrecipitationDepth.MILLIMETERS
    _attr_native_pressure_unit = UnitOfPressure.HPA
    _attr_native_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_native_wind_speed_unit = UnitOfSpeed.KILOMETERS_PER_HOUR
    _attr_supported_features = (
        WeatherEntityFeature.FORECAST_DAILY
    )

    def __init__(
        self,
        coordinator: WillyWeatherDataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the weather entity."""
        super().__init__(coordinator)
        self._station_id = entry.data[CONF_STATION_ID]
        self._station_name = entry.data.get(CONF_STATION_NAME, f"Station {self._station_id}")
        self._attr_unique_id = f"{self._station_id}_weather"
        self._entry = entry

        self._attr_device_info = DeviceInfo(
            entry_type=DeviceEntryType.SERVICE,
            identifiers={(DOMAIN, self._station_id)},
            manufacturer=MANUFACTURER,
            name=self._station_name,
        )

    @property
    def condition(self) -> str | None:
        """Return the current condition."""
        if not self.coordinator.data:
            return None

        try:
            forecasts = self.coordinator.data.get("forecast", {}).get("forecasts", {})
            weather_days = forecasts.get("weather", {}).get("days", [])
            
            if weather_days and weather_days[0].get("entries"):
                precis_code = weather_days[0]["entries"][0].get("precisCode")
                return CONDITION_MAP.get(precis_code, "unknown")
        except (KeyError, IndexError, TypeError):
            pass

        return None

    @property
    def native_temperature(self) -> float | None:
        """Return the temperature."""
        return self._get_observation_value(["temperature", "temperature"])

    @property
    def native_apparent_temperature(self) -> float | None:
        """Return the apparent temperature."""
        return self._get_observation_value(["temperature", "apparentTemperature"])

    @property
    def native_pressure(self) -> float | None:
        """Return the pressure."""
        return self._get_observation_value(["pressure", "pressure"])

    @property
    def humidity(self) -> float | None:
        """Return the humidity."""
        return self._get_observation_value(["humidity", "percentage"])

    @property
    def native_wind_speed(self) -> float | None:
        """Return the wind speed."""
        return self._get_observation_value(["wind", "speed"])

    @property
    def wind_bearing(self) -> float | str | None:
        """Return the wind bearing."""
        return self._get_observation_value(["wind", "direction"])

    @property
    def native_wind_gust_speed(self) -> float | None:
        """Return the wind gust speed."""
        return self._get_observation_value(["wind", "gustSpeed"])

    @property
    def cloud_coverage(self) -> float | None:
        """Return the cloud coverage in percentage."""
        # Convert oktas (0-8) to percentage (0-100)
        oktas = self._get_observation_value(["cloud", "oktas"])
        if oktas is not None:
            return (oktas / 8) * 100
        return None

    def _get_observation_value(self, path: list[str]) -> Any:
        """Get value from observational data using path."""
        if not self.coordinator.data:
            return None

        try:
            observations = self.coordinator.data.get("observational", {}).get("observations", {})
            value = observations
            for key in path:
                if isinstance(value, dict):
                    value = value.get(key)
                else:
                    return None
            return value
        except (KeyError, TypeError):
            return None

    @callback
    def _async_forecast_daily(self) -> list[Forecast] | None:
        """Return the daily forecast."""
        if not self.coordinator.data:
            return None

        try:
            forecasts = self.coordinator.data.get("forecast", {}).get("forecasts", {})
            weather_days = forecasts.get("weather", {}).get("days", [])

            # Check if rainfall is enabled
            rainfall_enabled = self._entry.options.get(CONF_FORECAST_RAINFALL, False)
            rainfall_days = forecasts.get("rainfall", {}).get("days", []) if rainfall_enabled else []
            
            # Check if UV is enabled
            uv_enabled = self._entry.options.get(CONF_FORECAST_UV, False)
            uv_days = forecasts.get("uv", {}).get("days", []) if uv_enabled else []

            forecast_data = []
            for idx, day in enumerate(weather_days):
                if not day.get("entries"):
                    continue

                entry = day["entries"][0]
                date_string = entry.get("dateTime")

                if not date_string:
                    continue

                # Parse datetime
                try:
                    dt = datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
                except ValueError:
                    continue

                forecast_dict: Forecast = {
                    "datetime": dt.isoformat(),
                    "temperature": entry.get("max"),
                    "templow": entry.get("min"),
                    "condition": CONDITION_MAP.get(entry.get("precisCode"), "unknown"),
                }

                # Add rainfall data if enabled
                if rainfall_enabled and idx < len(rainfall_days):
                    rainfall_day = rainfall_days[idx]
                    if rainfall_day.get("entries"):
                        rain_entry = rainfall_day["entries"][0]
                        start_range = rain_entry.get("startRange")
                        end_range = rain_entry.get("endRange")
                        if start_range is not None and end_range is not None:
                            forecast_dict["precipitation"] = (start_range + end_range) / 2
                        elif end_range is not None:
                            forecast_dict["precipitation"] = end_range
                        
                        rain_prob = rain_entry.get("probability")
                        if rain_prob is not None:
                            forecast_dict["precipitation_probability"] = rain_prob

                # Add UV data if enabled
                if uv_enabled and idx < len(uv_days):
                    uv_day = uv_days[idx]
                    if uv_day.get("entries"):
                        uv_entry = uv_day["entries"][0]
                        uv_index = uv_entry.get("index")
                        if uv_index is not None:
                            forecast_dict["uv_index"] = uv_index

                forecast_data.append(forecast_dict)

            return forecast_data if forecast_data else None

        except (KeyError, IndexError, TypeError, ValueError) as err:
            _LOGGER.error("Error parsing forecast data: %s", err)
            return None