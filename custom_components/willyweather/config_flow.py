"""Config flow for WillyWeather integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_API_KEY
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import config_validation as cv

from .const import (
    CONF_FORECAST_DAYS,
    CONF_FORECAST_RAINFALL,
    CONF_FORECAST_SUNRISESUNSET,
    CONF_FORECAST_TIDES,
    CONF_FORECAST_UV,
    CONF_SENSOR_FORMAT,
    CONF_STATION_ID,
    CONF_STATION_NAME,
    DEFAULT_FORECAST_DAYS,
    DOMAIN,
    SENSOR_FORMAT_BOM,
    SENSOR_FORMAT_DARKSKY,
)
from .coordinator import async_get_station_id, async_get_station_name

_LOGGER = logging.getLogger(__name__)


class WillyWeatherConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for WillyWeather."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step - API key and station."""
        errors = {}

        if user_input is not None:
            api_key = user_input[CONF_API_KEY]
            station_id = user_input.get(CONF_STATION_ID)

            _LOGGER.debug("Starting WillyWeather setup with API key: %s...", api_key[:10])
            
            # If no station_id provided, get from coordinates
            if not station_id:
                _LOGGER.info(
                    "No station ID provided, searching for closest station to lat=%s, lon=%s",
                    self.hass.config.latitude,
                    self.hass.config.longitude,
                )
                try:
                    station_id = await async_get_station_id(
                        self.hass,
                        self.hass.config.latitude,
                        self.hass.config.longitude,
                        api_key,
                    )
                    if not station_id:
                        _LOGGER.error("Could not find any station near the configured location")
                        errors["base"] = "no_station_found"
                    else:
                        _LOGGER.info("Found station ID: %s", station_id)
                except Exception as err:
                    _LOGGER.error("Error searching for station: %s", err, exc_info=True)
                    errors["base"] = "search_failed"
            else:
                _LOGGER.info("Using provided station ID: %s", station_id)

            # Get station name and verify API key works
            station_name = None
            if station_id and not errors:
                _LOGGER.debug("Fetching station name for ID: %s", station_id)
                try:
                    station_name = await async_get_station_name(self.hass, station_id, api_key)
                    if not station_name:
                        _LOGGER.error(
                            "Could not fetch station name. Check API key and station ID"
                        )
                        errors["base"] = "invalid_station_or_key"
                    else:
                        _LOGGER.info("Successfully connected to station: %s", station_name)
                except Exception as err:
                    _LOGGER.error("Error fetching station info: %s", err, exc_info=True)
                    errors["base"] = "api_error"

            if not errors:
                # Store data for next step
                self.init_data = {
                    CONF_API_KEY: api_key,
                    CONF_STATION_ID: station_id,
                    CONF_STATION_NAME: station_name,
                }
                return await self.async_step_forecasts()

        data_schema = vol.Schema(
            {
                vol.Required(CONF_API_KEY): cv.string,
                vol.Optional(CONF_STATION_ID): cv.string,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={
                "api_url": "https://www.willyweather.com.au/info/api.html"
            },
        )

    async def async_step_forecasts(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Configure forecast options."""
        if user_input is not None:
            await self.async_set_unique_id(f"{DOMAIN}_{self.init_data[CONF_STATION_ID]}")
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=self.init_data[CONF_STATION_NAME] or f"WillyWeather {self.init_data[CONF_STATION_ID]}",
                data=self.init_data,
                options={
                    CONF_SENSOR_FORMAT: user_input[CONF_SENSOR_FORMAT],
                    CONF_FORECAST_DAYS: user_input[CONF_FORECAST_DAYS],
                    CONF_FORECAST_RAINFALL: user_input.get(CONF_FORECAST_RAINFALL, False),
                    CONF_FORECAST_UV: user_input.get(CONF_FORECAST_UV, False),
                    CONF_FORECAST_SUNRISESUNSET: user_input.get(CONF_FORECAST_SUNRISESUNSET, False),
                    CONF_FORECAST_TIDES: user_input.get(CONF_FORECAST_TIDES, False),
                },
            )

        data_schema = vol.Schema(
            {
                vol.Required(CONF_SENSOR_FORMAT, default=SENSOR_FORMAT_DARKSKY): vol.In(
                    {
                        SENSOR_FORMAT_DARKSKY: "Dark Sky Compatible (for weather cards)",
                        SENSOR_FORMAT_BOM: "Bureau of Meteorology Compatible (for BoM weather card)",
                    }
                ),
                vol.Required(CONF_FORECAST_DAYS, default=DEFAULT_FORECAST_DAYS): vol.All(
                    vol.Coerce(int), vol.Range(min=1, max=7)
                ),
                vol.Optional(CONF_FORECAST_RAINFALL, default=False): cv.boolean,
                vol.Optional(CONF_FORECAST_UV, default=False): cv.boolean,
                vol.Optional(CONF_FORECAST_SUNRISESUNSET, default=False): cv.boolean,
                vol.Optional(CONF_FORECAST_TIDES, default=False): cv.boolean,
            }
        )

        return self.async_show_form(
            step_id="forecasts",
            data_schema=data_schema,
            description_placeholders={
                "station_name": self.init_data[CONF_STATION_NAME],
            },
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> WillyWeatherOptionsFlow:
        """Get the options flow for this handler."""
        return WillyWeatherOptionsFlow(config_entry)


class WillyWeatherOptionsFlow(config_entries.OptionsFlow):
    """Handle options flow for WillyWeather."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_SENSOR_FORMAT,
                        default=self.config_entry.options.get(CONF_SENSOR_FORMAT, SENSOR_FORMAT_DARKSKY),
                    ): vol.In(
                        {
                            SENSOR_FORMAT_DARKSKY: "Dark Sky Compatible (for weather cards)",
                            SENSOR_FORMAT_BOM: "Bureau of Meteorology Compatible (for BoM weather card)",
                        }
                    ),
                    vol.Required(
                        CONF_FORECAST_DAYS,
                        default=self.config_entry.options.get(CONF_FORECAST_DAYS, DEFAULT_FORECAST_DAYS),
                    ): vol.All(vol.Coerce(int), vol.Range(min=1, max=7)),
                    vol.Optional(
                        CONF_FORECAST_RAINFALL,
                        default=self.config_entry.options.get(CONF_FORECAST_RAINFALL, False),
                    ): cv.boolean,
                    vol.Optional(
                        CONF_FORECAST_UV,
                        default=self.config_entry.options.get(CONF_FORECAST_UV, False),
                    ): cv.boolean,
                    vol.Optional(
                        CONF_FORECAST_SUNRISESUNSET,
                        default=self.config_entry.options.get(CONF_FORECAST_SUNRISESUNSET, False),
                    ): cv.boolean,
                    vol.Optional(
                        CONF_FORECAST_TIDES,
                        default=self.config_entry.options.get(CONF_FORECAST_TIDES, False),
                    ): cv.boolean,
                }
            ),
        )