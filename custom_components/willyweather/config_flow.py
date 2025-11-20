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
    CONF_INCLUDE_WIND,
    CONF_INCLUDE_UV,
    CONF_INCLUDE_TIDES,
    CONF_INCLUDE_SWELL,
    CONF_STATION_ID,
    CONF_STATION_NAME,
    CONF_UPDATE_INTERVAL_DAY,
    CONF_UPDATE_INTERVAL_NIGHT,
    CONF_FORECAST_UPDATE_INTERVAL_DAY,
    CONF_FORECAST_UPDATE_INTERVAL_NIGHT,
    CONF_NIGHT_START_HOUR,
    CONF_NIGHT_END_HOUR,
    DEFAULT_UPDATE_INTERVAL_DAY,
    DEFAULT_UPDATE_INTERVAL_NIGHT,
    DEFAULT_FORECAST_UPDATE_INTERVAL_DAY,
    DEFAULT_FORECAST_UPDATE_INTERVAL_NIGHT,
    DEFAULT_NIGHT_START_HOUR,
    DEFAULT_NIGHT_END_HOUR,
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
        """Handle sensor options step."""
        if user_input is not None:
            self._sensor_options = user_input
            return await self.async_step_warnings()

        data_schema = vol.Schema(
            {
                vol.Required(CONF_INCLUDE_OBSERVATIONAL, default=True): cv.boolean,
                vol.Optional(CONF_INCLUDE_WIND, default=True): cv.boolean,
                vol.Optional(CONF_INCLUDE_UV, default=True): cv.boolean,
                vol.Optional(CONF_INCLUDE_TIDES, default=False): cv.boolean,
                vol.Optional(CONF_INCLUDE_SWELL, default=False): cv.boolean,
            }
        )

        return self.async_show_form(
            step_id="options",
            data_schema=data_schema,
            description_placeholders={"station_name": self._station_name},
        )

    async def async_step_warnings(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle warning options step."""
        if user_input is not None:
            self._warning_options = user_input
            return await self.async_step_update_intervals()

        data_schema = vol.Schema(
            {
                vol.Required(CONF_INCLUDE_WARNINGS, default=True): cv.boolean,
            }
        )

        return self.async_show_form(
            step_id="warnings",
            data_schema=data_schema,
            description_placeholders={"station_name": self._station_name},
        )

    async def async_step_update_intervals(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle update interval configuration step."""
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
                    CONF_INCLUDE_OBSERVATIONAL: self._sensor_options.get(CONF_INCLUDE_OBSERVATIONAL, True),
                    CONF_INCLUDE_WIND: self._sensor_options.get(CONF_INCLUDE_WIND, True),
                    CONF_INCLUDE_UV: self._sensor_options.get(CONF_INCLUDE_UV, True),
                    CONF_INCLUDE_TIDES: self._sensor_options.get(CONF_INCLUDE_TIDES, False),
                    CONF_INCLUDE_SWELL: self._sensor_options.get(CONF_INCLUDE_SWELL, False),
                    CONF_INCLUDE_WARNINGS: self._warning_options.get(CONF_INCLUDE_WARNINGS, True),
                    CONF_UPDATE_INTERVAL_DAY: user_input.get(CONF_UPDATE_INTERVAL_DAY, DEFAULT_UPDATE_INTERVAL_DAY),
                    CONF_UPDATE_INTERVAL_NIGHT: user_input.get(CONF_UPDATE_INTERVAL_NIGHT, DEFAULT_UPDATE_INTERVAL_NIGHT),
                    CONF_FORECAST_UPDATE_INTERVAL_DAY: user_input.get(CONF_FORECAST_UPDATE_INTERVAL_DAY, DEFAULT_FORECAST_UPDATE_INTERVAL_DAY),
                    CONF_FORECAST_UPDATE_INTERVAL_NIGHT: user_input.get(CONF_FORECAST_UPDATE_INTERVAL_NIGHT, DEFAULT_FORECAST_UPDATE_INTERVAL_NIGHT),
                    CONF_NIGHT_START_HOUR: user_input.get(CONF_NIGHT_START_HOUR, DEFAULT_NIGHT_START_HOUR),
                    CONF_NIGHT_END_HOUR: user_input.get(CONF_NIGHT_END_HOUR, DEFAULT_NIGHT_END_HOUR),
                },
            )

        data_schema = vol.Schema(
            {
                vol.Required(CONF_UPDATE_INTERVAL_DAY, default=DEFAULT_UPDATE_INTERVAL_DAY): vol.All(
                    vol.Coerce(int), vol.Range(min=5, max=60)
                ),
                vol.Required(CONF_UPDATE_INTERVAL_NIGHT, default=DEFAULT_UPDATE_INTERVAL_NIGHT): vol.All(
                    vol.Coerce(int), vol.Range(min=10, max=120)
                ),
                vol.Required(CONF_FORECAST_UPDATE_INTERVAL_DAY, default=DEFAULT_FORECAST_UPDATE_INTERVAL_DAY): vol.All(
                    vol.Coerce(int), vol.Range(min=30, max=240)
                ),
                vol.Required(CONF_FORECAST_UPDATE_INTERVAL_NIGHT, default=DEFAULT_FORECAST_UPDATE_INTERVAL_NIGHT): vol.All(
                    vol.Coerce(int), vol.Range(min=60, max=480)
                ),
                vol.Required(CONF_NIGHT_START_HOUR, default=DEFAULT_NIGHT_START_HOUR): vol.All(
                    vol.Coerce(int), vol.Range(min=0, max=23)
                ),
                vol.Required(CONF_NIGHT_END_HOUR, default=DEFAULT_NIGHT_END_HOUR): vol.All(
                    vol.Coerce(int), vol.Range(min=0, max=23)
                ),
            }
        )

        return self.async_show_form(
            step_id="update_intervals",
            data_schema=data_schema,
            description_placeholders={"station_name": self._station_name},
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
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
        """Manage the options for sensors."""
        if user_input is not None:
            self._sensor_options = user_input
            return await self.async_step_warnings()

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
                    vol.Optional(
                        CONF_INCLUDE_WIND,
                        default=self.config_entry.options.get(CONF_INCLUDE_WIND, True),
                    ): cv.boolean,
                    vol.Optional(
                        CONF_INCLUDE_UV,
                        default=self.config_entry.options.get(CONF_INCLUDE_UV, True),
                    ): cv.boolean,
                    vol.Optional(
                        CONF_INCLUDE_TIDES,
                        default=self.config_entry.options.get(CONF_INCLUDE_TIDES, False),
                    ): cv.boolean,
                    vol.Optional(
                        CONF_INCLUDE_SWELL,
                        default=self.config_entry.options.get(CONF_INCLUDE_SWELL, False),
                    ): cv.boolean,
                }
            ),
        )

    async def async_step_warnings(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the warning options."""
        if user_input is not None:
            self._warning_options = user_input
            return await self.async_step_update_intervals()

        return self.async_show_form(
            step_id="warnings",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_INCLUDE_WARNINGS,
                        default=self.config_entry.options.get(CONF_INCLUDE_WARNINGS, True),
                    ): cv.boolean,
                }
            ),
        )

    async def async_step_update_intervals(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the update interval options."""
        if user_input is not None:
            # Merge all options together
            return self.async_create_entry(
                title="",
                data={
                    **self._sensor_options,
                    **self._warning_options,
                    CONF_UPDATE_INTERVAL_DAY: user_input.get(
                        CONF_UPDATE_INTERVAL_DAY, DEFAULT_UPDATE_INTERVAL_DAY
                    ),
                    CONF_UPDATE_INTERVAL_NIGHT: user_input.get(
                        CONF_UPDATE_INTERVAL_NIGHT, DEFAULT_UPDATE_INTERVAL_NIGHT
                    ),
                    CONF_FORECAST_UPDATE_INTERVAL_DAY: user_input.get(
                        CONF_FORECAST_UPDATE_INTERVAL_DAY, DEFAULT_FORECAST_UPDATE_INTERVAL_DAY
                    ),
                    CONF_FORECAST_UPDATE_INTERVAL_NIGHT: user_input.get(
                        CONF_FORECAST_UPDATE_INTERVAL_NIGHT, DEFAULT_FORECAST_UPDATE_INTERVAL_NIGHT
                    ),
                    CONF_NIGHT_START_HOUR: user_input.get(
                        CONF_NIGHT_START_HOUR, DEFAULT_NIGHT_START_HOUR
                    ),
                    CONF_NIGHT_END_HOUR: user_input.get(
                        CONF_NIGHT_END_HOUR, DEFAULT_NIGHT_END_HOUR
                    ),
                },
            )

        return self.async_show_form(
            step_id="update_intervals",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_UPDATE_INTERVAL_DAY,
                        default=self.config_entry.options.get(
                            CONF_UPDATE_INTERVAL_DAY, DEFAULT_UPDATE_INTERVAL_DAY
                        ),
                    ): vol.All(vol.Coerce(int), vol.Range(min=5, max=60)),
                    vol.Required(
                        CONF_UPDATE_INTERVAL_NIGHT,
                        default=self.config_entry.options.get(
                            CONF_UPDATE_INTERVAL_NIGHT, DEFAULT_UPDATE_INTERVAL_NIGHT
                        ),
                    ): vol.All(vol.Coerce(int), vol.Range(min=10, max=120)),
                    vol.Required(
                        CONF_FORECAST_UPDATE_INTERVAL_DAY,
                        default=self.config_entry.options.get(
                            CONF_FORECAST_UPDATE_INTERVAL_DAY, DEFAULT_FORECAST_UPDATE_INTERVAL_DAY
                        ),
                    ): vol.All(vol.Coerce(int), vol.Range(min=30, max=240)),
                    vol.Required(
                        CONF_FORECAST_UPDATE_INTERVAL_NIGHT,
                        default=self.config_entry.options.get(
                            CONF_FORECAST_UPDATE_INTERVAL_NIGHT, DEFAULT_FORECAST_UPDATE_INTERVAL_NIGHT
                        ),
                    ): vol.All(vol.Coerce(int), vol.Range(min=60, max=480)),
                    vol.Required(
                        CONF_NIGHT_START_HOUR,
                        default=self.config_entry.options.get(
                            CONF_NIGHT_START_HOUR, DEFAULT_NIGHT_START_HOUR
                        ),
                    ): vol.All(vol.Coerce(int), vol.Range(min=0, max=23)),
                    vol.Required(
                        CONF_NIGHT_END_HOUR,
                        default=self.config_entry.options.get(
                            CONF_NIGHT_END_HOUR, DEFAULT_NIGHT_END_HOUR
                        ),
                    ): vol.All(vol.Coerce(int), vol.Range(min=0, max=23)),
                }
            ),
        )