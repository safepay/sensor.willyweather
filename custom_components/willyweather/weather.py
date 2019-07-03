"""Support for the WillyWeather Australia service."""
import logging
from datetime import timedelta

import requests
import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from homeassistant.components.weather import (
    ATTR_FORECAST_CONDITION, ATTR_FORECAST_TEMP, ATTR_FORECAST_TEMP_LOW,
    ATTR_FORECAST_TIME, PLATFORM_SCHEMA, WeatherEntity)
from homeassistant.const import (TEMP_CELSIUS, CONF_NAME, STATE_UNKNOWN)
from homeassistant.util import Throttle

_RESOURCE = 'https://api.willyweather.com.au/v2/{}/locations/{}/weather.json?observational=true&forecasts=weather&days=4'
_CLOSEST =  'https://api.willyweather.com.au/v2/{}/search.json'
_LOGGER = logging.getLogger(__name__)

ATTRIBUTION = "Weather details provided by WillyWeather Australia."

#CONF_FORECAST = 'forecast'
CONF_STATION_ID = 'station_id'
CONF_API_KEY = 'api_key'

DEFAULT_NAME = 'WW'

MIN_TIME_BETWEEN_UPDATES = timedelta(minutes=60)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_API_KEY): cv.string,
    vol.Optional(CONF_STATION_ID): cv.string,
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
})


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the WillyWeather weather sensor."""

    unit = hass.config.units.temperature_unit
    station_id = config.get(CONF_STATION_ID)
    api_key = config.get(CONF_API_KEY)
    #forecast = config.get(CONF_FORECAST)
    name = config.get(CONF_NAME)

    # If no station_id determine from Home Assistant lat/long
    if station_id is None:
        station_id = get_station_id(hass.config.latitude, hass.config.longitude, api_key)
        if station_id is None:
            _LOGGER.critical("Can't retrieve Station from WillyWeather")
            return False

    ww_data = WeatherData(api_key, station_id)

    try:
        ww_data.update()
    except ValueError as err:
        _LOGGER.error("Received error from WillyWeather: %s", err)
        return

    add_entities([WWWeatherForecast(ww_data, name, unit)], True)


class WWWeatherForecast(WeatherEntity):
    """Implementation of the WillyWeather weather sensor."""

    def __init__(self, weather_data, name, unit):
        """Initialize the component."""
        self._name = name
        self._data = weather_data
        self._unit = unit
#        _LOGGER.critical("!!!!!!!!!!!!!!!!!!!!!!!HUMIDITY!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! %s", self._data.latest_data['observational']["observations"]["humidity"].get("percentage"))

    @property
    def name(self):
        """Return the name."""
        return self._name

    @property
    def condition(self):
        """Return the current condition."""
        return self._data.latest_data['forecasts']["weather"]["days"][0]["entries"][0].get("precisCode")

    @property
    def temperature(self):
        """Return the temperature."""
        return self._data.latest_data['observational']["observations"]["temperature"].get("temperature")

    @property
    def pressure(self):
        """Return the pressure."""
        return self._data.latest_data['observational']["observations"]["pressure"].get("pressure")

    @property
    def humidity(self):
        """Return the humidity."""
        return self._data.latest_data['observational']["observations"]["humidity"].get("percentage")

    @property
    def wind_speed(self):
        """Return the wind speed."""
        return self._data.latest_data['observational']["observations"]["wind"].get("speed")

    @property
    def wind_bearing(self):
        """Return the wind direction."""
        return self._data.latest_data['observational']["observations"]["wind"].get("directionText")

    @property
    def attribution(self):
        """Return the attribution."""
        return ATTRIBUTION

    @property
    def temperature_unit(self):
        """Return the unit of measurement."""
        return self._unit

    def update(self):
        """Get the latest data from WillyWeather and updates the states."""
        self._data.update()
        if not self._data:
            _LOGGER.info("Didn't receive weather data from WillyWeather")
            return

class WeatherData:
    """Handle WillyWeather API object and limit updates."""

    def __init__(self, api_key, station_id):
        """Initialize the data object."""
        self._api_key = api_key
        self._station_id = station_id

    def _build_url(self):
        """Build the URL for the requests."""
        url = _RESOURCE.format(self._api_key, self._station_id)
        _LOGGER.debug("WillyWeather URL: %s", url)
        return url

    @property
    def latest_data(self):
        """Return the latest data object."""
        if self._data:
            return self._data
        return None

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    def update(self):
        """Get the latest data from WillyWeather."""
        result = requests.get(self._build_url(), timeout=10).json()
        self._data = result
        return

def get_station_id(lat, lng, api_key):

    closestURL = _CLOSEST.format(api_key)
    closestURLParams = [
        ("lat", lat),
        ("lng", lng),
        ("units", "distance:km")
    ]

    try:
        resp = requests.get(closestURL, params=closestURLParams, timeout=10).json()
        if resp is None:
            return

        return resp['location']['id']

    except ValueError as err:
        _LOGGER.error("*** Error finding closest station")
