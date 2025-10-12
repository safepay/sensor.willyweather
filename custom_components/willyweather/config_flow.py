"""Config flow for WillyWeather integration."""
import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
import homeassistant.helpers.config_validation as cv

from .const import CONF_API_KEY, CONF_DAYS, CONF_STATION_ID, DEFAULT_DAYS, DOMAIN
from .coordinator import async_get_station_id

_LOGGER = logging.getLogger(__name__)


def validate_days(days: int) -> int:
    """Check that days is within bounds."""
    if days not in range(1, 8):
        raise vol.Invalid("Days must be between 1 and 7")
    return days


class WillyWeatherConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for WillyWeather."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            api_key = user_input[CONF_API_KEY]
            station_id = user_input.get(CONF_STATION_ID)
            days = user_input.get(CONF_DAYS, DEFAULT_DAYS)

            # If no station_id, get from coordinates
            if not station_id:
                station_id = await async_get_station_id(
                    self.hass,
                    self.hass.config.latitude,
                    self.hass.config.longitude,
                    api_key,
                )
                if not station_id:
                    errors["base"] = "cannot_connect"

            if not errors:
                await self.async_set_unique_id(f"{DOMAIN}_{station_id}")
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=f"WillyWeather {station_id}",
                    data={
                        CONF_API_KEY: api_key,
                        CONF_STATION_ID: station_id,
                        CONF_DAYS: days,
                    },
                )

        data_schema = vol.Schema(
            {
                vol.Required(CONF_API_KEY): cv.string,
                vol.Optional(CONF_STATION_ID): cv.string,
                vol.Optional(CONF_DAYS, default=DEFAULT_DAYS): vol.All(
                    vol.Coerce(int), validate_days
                ),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )
