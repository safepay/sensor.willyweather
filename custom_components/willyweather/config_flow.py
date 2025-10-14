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

    def __init__(self) -> None:
        """Initialize."""
        self._api_key: str = ""
        self._station_id: str = ""
        self._station_name: str = ""

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle user step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            self._api_key = user_input[CONF_API_KEY].strip()
            station_id = user_input.get(CONF_STATION_ID, "").strip()

            _LOGGER.debug("Starting WillyWeather setup")
            
            # Auto-detect station if not provided
            if not station_id:
                _LOGGER.info("Auto-detecting station")
                try:
                    station_id = await async_get_station_id(
                        self.hass,
                        self.hass.config.latitude,
                        self.hass.config.longitude,
                        self._api_key,
                    )
                    if not station_id:
                        errors["base"] = "no_station_found"
                except Exception as err:
                    _LOGGER.error("Error auto-detecting station: %s", err)
                    errors["base"] = "search_failed"
            
            # Get station name
            if not errors and station_id:
                try:
                    station_name = await async_get_station_name(
                        self.hass, station_id, self._api_key
                    )
                    if not station_name:
                        errors["base"] = "invalid_station_or_key"
                    else:
                        self._station_id = station_id
                        self._station_name = station_name
                        return await self.async_step_options()
                except Exception as err:
                    _LOGGER.error("Error fetching station name: %s", err)
                    errors["base"] = "api_error"

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

    async def async_step_options(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle options step."""
        if user_input is not None:
            await self.async_set_unique_id(f"{DOMAIN}_{self._station_id}")
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=self._station_name or f"Station {self._station_id}",
                data={
                    CONF_API_KEY: self._api_key,
                    CONF_STATION_ID: self._station_id,
                    CONF_STATION_NAME: self._station_name,
                },
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
            step_id="options",
            data_schema=data_schema,
            description_placeholders={"station_name": self._station_name},
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
                        default=self.config_entry.options.get(
                            CONF_INCLUDE_OBSERVATIONAL, True
                        ),
                    ): cv.boolean,
                    vol.Required(
                        CONF_INCLUDE_WARNINGS,
                        default=self.config_entry.options.get(
                            CONF_INCLUDE_WARNINGS, False
                        ),
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
            ),
        )