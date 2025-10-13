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
    CONF_INCLUDE_OBSERVATIONAL,
    CONF_INCLUDE_WARNINGS,
    CONF_ADDITIONAL_FORECAST,
    CONF_INCLUDE_UV,
    CONF_INCLUDE_TIDES,
    CONF_INCLUDE_WIND,
    CONF_STATION_ID,
    CONF_STATION_NAME,
    DOMAIN,
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
                return await self.async_step_sensors()

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

    async def async_step_sensors(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Configure sensor options."""
        if user_input is not None:
            await self.async_set_unique_id(f"{DOMAIN}_{self.init_data[CONF_STATION_ID]}")
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=self.init_data[CONF_STATION_NAME] or f"WillyWeather {self.init_data[CONF_STATION_ID]}",
                data=self.init_data,
                options={
                    CONF_INCLUDE_OBSERVATIONAL: user_input.get(CONF_INCLUDE_OBSERVATIONAL, True),
                    CONF_INCLUDE_WARNINGS: user_input.get(CONF_INCLUDE_WARNINGS, False),
                    CONF_INCLUDE_UV: user_input.get(CONF_INCLUDE_UV, False),
                    CONF_INCLUDE_TIDES: user_input.get(CONF_INCLUDE_TIDES, False),
                    CONF_INCLUDE_WIND: user_input.get(CONF_INCLUDE_WIND, False),
                },
            )

        data_schema = vol.Schema(
            {
                vol.Required(CONF_INCLUDE_OBSERVATIONAL, default=True): cv.boolean,
                vol.Required(CONF_INCLUDE_WARNINGS, default=False): cv.boolean,
                vol.Optional(CONF_INCLUDE_UV, default=False): cv.boolean,
                vol.Optional(CONF_INCLUDE_TIDES, default=False): cv.boolean,
                vol.Optional(CONF_INCLUDE_WIND, default=False): cv.boolean,
            }
        )

        return self.async_show_form(
            step_id="sensors",
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
                        CONF_INCLUDE_OBSERVATIONAL,
                        default=self.config_entry.options.get(CONF_INCLUDE_OBSERVATIONAL, True),
                    ): cv.boolean,
                    vol.Required(
                        CONF_INCLUDE_WARNINGS,
                        default=self.config_entry.options.get(CONF_INCLUDE_WARNINGS, False),
                    ): cv.boolean,
                    vol.Optional(
                        CONF_INCLUDE_UV,
                        default=self.config_entry.options.get(CONF_INCLUDE_UV, False),
                    ): cv.boolean,
                    vol.Optional(
                        CONF_INCLUDE_TIDES,
                        default=self.config_entry.options.get(CONF_INCLUDE_TIDES, False),
                    ): cv.boolean,
                    vol.Optional(
                        CONF_INCLUDE_WIND,
                        default=self.config_entry.options.get(CONF_INCLUDE_WIND, False),
                    ): cv.boolean,
                }
            ),        )