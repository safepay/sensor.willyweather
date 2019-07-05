"""Support for the WillyWeather Australia service."""
import logging
from datetime import timedelta

import requests
import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.const import (
    TEMP_CELSIUS, CONF_MONITORED_CONDITIONS, CONF_NAME,
    ATTR_ATTRIBUTION)
from homeassistant.helpers.entity import Entity
from homeassistant.util import Throttle

_RESOURCE = 'https://api.willyweather.com.au/v2/{}/locations/{}/weather.json?observational=true'
_CLOSEST =  'https://api.willyweather.com.au/v2/{}/search.json'
_LOGGER = logging.getLogger(__name__)

ATTRIBUTION = "Weather details provided by WillyWeather Australia."

CONF_STATION_ID = 'station_id'
CONF_API_KEY = 'api_key'

DEFAULT_NAME = 'WW'

MIN_TIME_BETWEEN_UPDATES = timedelta(minutes=10)

SENSOR_TYPES = {
    'temperature': ['Temperature', TEMP_CELSIUS, 'mdi:thermometer'],
    'apparent_temperature': ['Feels like', TEMP_CELSIUS, 'mdi:thermometer'],
    'cloud': ['Cloud', 'okta', 'mdi:weather-partlycloudy'],
    'humidity': ['Humidity', '%', 'mdi:water-percent'],
    'dewpoint': ['Dew point', TEMP_CELSIUS, 'mdi:thermometer'],
    'pressure': ['Pressure', 'hPa', 'mdi:gauge'],
    'wind_speed': ['Wind speed', 'km/h', 'mdi:weather-windy'],
    'wind_gust': ['Wind gust', 'km/h', 'mdi:weather-windy-variant'],
    'wind_direction': ['Wind direction', None, 'mdi:compass'],
    'rainlasthour': ['Rain last hour', 'mm', 'mdi:weather-rainy'],
    'raintoday': ['Rain today', 'mm', 'mdi:weather-rainy'],
    'rainsince9am': ['Rain since 9am', 'mm', 'mdi:weather-rainy']
}

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_API_KEY): cv.string,
    vol.Optional(CONF_STATION_ID): cv.string,
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Required(CONF_MONITORED_CONDITIONS, default=list(SENSOR_TYPES)):
        vol.All(cv.ensure_list, [vol.In(SENSOR_TYPES)]),
})


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the WillyWeather weather sensor."""

    station_id = config.get(CONF_STATION_ID)
    api_key = config.get(CONF_API_KEY)
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

    dev = []
    for variable in config[CONF_MONITORED_CONDITIONS]:
        dev.append(WWWeatherSensor(ww_data, name, variable))

    add_entities(dev, True)


class WWWeatherSensor(Entity):
    """Implementation of the WillyWeather weather sensor."""

    def __init__(self, weather_data, name, sensor_type):
        """Initialize the sensor."""
        self._client = name
        self._name = SENSOR_TYPES[sensor_type][0]
        self._type = sensor_type
        self._state = None
        self._unit = SENSOR_TYPES[sensor_type][1]
        self._data = weather_data
        self._code = None
        self._icon = SENSOR_TYPES[sensor_type][2]

    @property
    def name(self):
        """Return the name of the sensor."""
        return '{} {}'.format(self._client, self._name)

    @property
    def state(self):
        """Return the state of the device."""
        return self._state

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement of this entity, if any."""
        return self._unit

    @property
    def device_state_attributes(self):
        """Return the state attributes."""
        attrs = {ATTR_ATTRIBUTION: ATTRIBUTION}
        return attrs

    @property
    def icon(self):
        """Icon to use in the frontend, if any."""
        return self._icon

    def update(self):
        """Get the latest data from WillyWeather and updates the states."""
        self._data.update()
        if not self._data:
            _LOGGER.info("Didn't receive weather data from WillyWeather")
            return

        # Read data
        if self._type == 'temperature':
            self._state = self._data.latest_data["observations"]["temperature"].get("temperature")
        elif self._type == 'apparent_temperature':
            self._state = self._data.latest_data["observations"]["temperature"].get("apparentTemperature")
        elif self._type == 'cloud':
            self._state = self._data.latest_data["observations"]["cloud"].get("oktas")
        elif self._type == 'humidity':
            self._state = self._data.latest_data["observations"]["humidity"].get("percentage")
        elif self._type == 'depoint':
            self._state = self._data.latest_data["observations"]["dewPoint"].get("temperature")
        elif self._type == 'pressure':
            self._state = self._data.latest_data["observations"]["pressure"].get("pressure")
        elif self._type == 'wind_speed':
            self._state = self._data.latest_data["observations"]["wind"].get("speed")
        elif self._type == 'wind_gust':
            self._state = self._data.latest_data["observations"]["wind"].get("gustSpeed")
        elif self._type == 'wind_direction':
            self._state = self._data.latest_data["observations"]["wind"].get("directionText")
        elif self._type == 'rainlasthour':
            self._state = self._data.latest_data["observations"]["rainfall"].get("lastHourAmount")
        elif self._type == 'raintoday':
            self._state = self._data.latest_data["observations"]["rainfall"].get("todayAmount")
        elif self._type == 'rainsince9am':
            self._state = self._data.latest_data["observations"]["rainfall"].get("since9AMAmount")


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
        self._data = result['observational']
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
