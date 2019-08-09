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
_FORECAST_URL = 'https://api.willyweather.com.au/v2/{}/locations/{}/weather.json?forecasts=weather,rainfall&days={}'
_CLOSEST =  'https://api.willyweather.com.au/v2/{}/search.json'
_LOGGER = logging.getLogger(__name__)

ATTRIBUTION = "Data provided by WillyWeather"

CONF_STATION_ID = 'station_id'
CONF_API_KEY = 'api_key'
CONF_DAYS = 'forecast_days'

DEFAULT_NAME = 'WW'

MIN_TIME_BETWEEN_UPDATES = timedelta(minutes=30)

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

FORECAST_TYPES = {
    'forecast_maxtemp' : ['Max Temp', TEMP_CELSIUS, 'mdi:thermometer'],
    'forecast_mintemp' : ['Min Temp', TEMP_CELSIUS, 'mdi:thermometer'],
    'forecast_rain': ['Rain', 'mm', 'mdi:weather-rainy'],
    'forecast_rain_prob': ['Rain Probability', '%', 'mdi:weather-rainy'],
    'forecast_summary': ['Summary', '', ''],
    'forecast_icon': ['Icon', '', '']
}

MAP_CONDITION = {
'fine' : 'sunny',
'mostly-fine' : 'sunny',
'high-cloud' : 'partlycloudy',
'partly-cloudy' : 'partlycloudy',
'mostly-cloudy' : 'cloudy',
'cloudy' : 'cloudy',
'overcast' : 'cloudy',
'shower-or-two' : 'rainy',
'chance-shower-fine' : 'rainy',
'chance-shower-cloud' : 'rainy',
'drizzle' : 'rainy',
'few-showers' : 'rainy',
'showers-rain' : 'rainy',
'heavy-showers-rain' : 'rainy',
'chance-thunderstorm-fine' : 'lightning',
'chance-thunderstorm-cloud' : 'lightning',
'chance-thunderstorm-showers' :  'lightning-rainy',
'thunderstorm' : 'lightning-rainy',
'chance-snow-fine' : 'snowy',
'chance-snow-cloud' : 'snowy',
'snow-and-rain' : 'snowy-rainy',
'light-snow' : 'snowy',
'snow' : 'snowy',
'heavy-snow' : 'snowy',
'wind' : 'windy',
'frost' : 'clear-night',
'fog' : 'fog',
'hail' : 'hail',
'dust' : None
}


DARK_SKY_ICONS = {
'fine' : 'clear-day',
'mostly-fine' : 'clear-day',
'high-cloud' : 'partly-cloudy-day',
'partly-cloudy' : 'partly-cloudy-day',
'mostly-cloudy' : 'partly-cloudy-day',
'cloudy' : 'partly-cloudy-day',
'overcast' : 'partly-cloudy-day',
'shower-or-two' : 'rain',
'chance-shower-fine' : 'rain',
'chance-shower-cloud' : 'rain',
'drizzle' : 'rain',
'few-showers' : 'rain',
'showers-rain' : 'rain',
'heavy-showers-rain' : 'rain',
'chance-thunderstorm-fine' : 'lightning',
'chance-thunderstorm-cloud' : 'lightning',
'chance-thunderstorm-showers' :  'lightning',
'thunderstorm' : 'thunderstorm',
'chance-snow-fine' : 'snow',
'chance-snow-cloud' : 'snow',
'snow-and-rain' : 'snow',
'light-snow' : 'snow',
'snow' : 'snow',
'heavy-snow' : 'snow',
'wind' : 'wind',
'frost' : 'clear-night',
'fog' : 'fog',
'hail' : 'hail',
'dust' : None
}


def validate_days(days):
    """Check that days is within bounds."""
    if days is not None and days not in range(1,8):
        raise vol.error.Invalid("Days is out of Range")
    return days

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_API_KEY): cv.string,
    vol.Optional(CONF_STATION_ID): cv.string,
    vol.Optional(CONF_DAYS, default=None): validate_days,
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
    vol.Required(CONF_MONITORED_CONDITIONS, default=list(SENSOR_TYPES)):
        vol.All(cv.ensure_list, [vol.In(SENSOR_TYPES)]),
})


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the WillyWeather weather sensor."""

    station_id = config.get(CONF_STATION_ID)
    api_key = config.get(CONF_API_KEY)
    name = config.get(CONF_NAME)
    days = config.get(CONF_DAYS)

    # If no station_id determine from Home Assistant lat/long
    if station_id is None:
        station_id = get_station_id(hass.config.latitude, hass.config.longitude, api_key)
        if station_id is None:
            _LOGGER.critical("Can't retrieve Station from WillyWeather")
            return False

    ww_data = WeatherData(api_key, station_id)

    try:
        await ww_data.async_update()
    except ValueError as err:
        _LOGGER.error("Received error from WillyWeather: %s", err)
        return

    dev = []
    for variable in config[CONF_MONITORED_CONDITIONS]:
        dev.append(WWWeatherSensor(ww_data, name, variable))

    if days:
        ww_forecast = ForecastData(api_key, station_id, days)
        try:
            await ww_forecast.async_update()
        except ValueError as err:
            _LOGGER.error("Received error from WillyWeather: %s", err)
            return

        for day, v in enumerate(ww_forecast.latest_data['forecasts']["weather"]["days"]):
            for variable in FORECAST_TYPES:
                dev.append(WWWeatherSensor(ww_forecast, name, variable, day))

    async_add_entities(dev, True)


class WWWeatherSensor(Entity):
    """Implementation of the WillyWeather weather sensor."""

    def __init__(self, weather_data, name, sensor_type, day=None):
        """Initialize the sensor."""
        self._client = name
        if day is not None:
            self._name = FORECAST_TYPES[sensor_type][0]
            self._unit = FORECAST_TYPES[sensor_type][1]
            self._icon = FORECAST_TYPES[sensor_type][2]
        else:
            self._name = SENSOR_TYPES[sensor_type][0]
            self._unit = SENSOR_TYPES[sensor_type][1]
            self._icon = SENSOR_TYPES[sensor_type][2]
        self._type = sensor_type
        self._state = None
        self._data = weather_data
        self._code = None
        self._day = day

    @property
    def name(self):
        """Return the name of the sensor."""
        if self._day is not None:
            return '{} Day {} {}'.format(self._client, self._day, self._name)
        else:
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

    async def async_update(self):
        """Get the latest data from WillyWeather and updates the states."""
        await self._data.async_update()
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
        elif self._type == 'forecast_maxtemp':
            self._state = self._data.latest_data['forecasts']['weather']['days'][self._day]['entries'][0].get('max')
        elif self._type == 'forecast_mintemp':
            self._state = self._data.latest_data['forecasts']['weather']['days'][self._day]['entries'][0].get('min')
        elif self._type == 'forecast_summary':
            self._state = self._data.latest_data['forecasts']['weather']['days'][self._day]['entries'][0].get('precis')
        elif self._type == 'forecast_rain':
            self._state = self._data.latest_data['forecasts']['rainfall']['days'][self._day]['entries'][0].get('endRange')
        elif self._type == 'forecast_rain_prob':
            self._state = self._data.latest_data['forecasts']['rainfall']['days'][self._day]['entries'][0].get('probability')
        elif self._type == 'forecast_condition':
            self._state = MAP_CONDITION.get(self._data.latest_data['forecasts']['weather']['days'][self._day]["entries"][0].get("precisCode"))
        elif self._type == 'forecast_icon':
            self._state = DARK_SKY_ICONS.get(self._data.latest_data['forecasts']['weather']['days'][self._day]["entries"][0].get("precisCode"))

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
    async def async_update(self):
        """Get the latest data from WillyWeather."""
        result = requests.get(self._build_url(), timeout=10).json()
        self._data = result['observational']
        return

class ForecastData:
    """Handle WillyWeather API object and limit updates."""

    def __init__(self, api_key, station_id, days):
        """Initialize the data object."""
        self._api_key = api_key
        self._station_id = station_id
        self._days = days

    def _build_url(self):
        """Build the URL for the requests."""
        url = _FORECAST_URL.format(self._api_key, self._station_id, self._days)
        _LOGGER.debug("WillyWeather URL: %s", url)
        return url

    @property
    def latest_data(self):
        """Return the latest data object."""
        if self._data:
            return self._data
        return None

    @Throttle(MIN_TIME_BETWEEN_UPDATES)
    async def async_update(self):
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
