"""Support for the WillyWeather Australia service."""
import logging
from datetime import datetime, timedelta

import requests
import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from homeassistant.components.weather import (
    ATTR_FORECAST_CONDITION, ATTR_FORECAST_TEMP, ATTR_FORECAST_TEMP_LOW, ATTR_FORECAST_PRECIPITATION,
    ATTR_FORECAST_TIME, PLATFORM_SCHEMA, WeatherEntity)
from homeassistant.const import (TEMP_CELSIUS, CONF_NAME, STATE_UNKNOWN)
from homeassistant.util import Throttle
_RESOURCE = 'https://api.willyweather.com.au/v2/{}/locations/{}/weather.json?observational=true&forecasts=weather,rainfall&days={}'
_CLOSEST =  'https://api.willyweather.com.au/v2/{}/search.json'
_LOGGER = logging.getLogger(__name__)

ATTRIBUTION = "Data provided by WillyWeather"

CONF_DAYS = 'days'
CONF_STATION_ID = 'station_id'
CONF_API_KEY = 'api_key'

DEFAULT_NAME = 'WW'

MIN_TIME_BETWEEN_UPDATES = timedelta(minutes=30)

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
'heavy-showers-rain' : 'pouring',
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
'dust' : 'exceptional'
}

def validate_days(days):
    """Check that days is within bounds."""
    if days not in range(1,7):
        raise vol.error.Invalid("Days is out of Range")
    return days
    
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_API_KEY): cv.string,
    vol.Optional(CONF_STATION_ID): cv.string,
    vol.Optional(CONF_DAYS, default=5): validate_days,
    vol.Optional(CONF_NAME, default=DEFAULT_NAME): cv.string,
})

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the WillyWeather weather sensor."""

    unit = hass.config.units.temperature_unit
    station_id = config.get(CONF_STATION_ID)
    api_key = config.get(CONF_API_KEY)
    days = config.get(CONF_DAYS)
    name = config.get(CONF_NAME)

    # If no station_id determine from Home Assistant lat/long
    if station_id is None:
        station_id = get_station_id(hass.config.latitude, hass.config.longitude, api_key)
        if station_id is None:
            _LOGGER.critical("Can't retrieve Station from WillyWeather")
            return False

    ww_data = WeatherData(api_key, station_id, days)

    try:
        await ww_data.async_update()
    except ValueError as err:
        _LOGGER.error("Received error from WillyWeather: %s", err)
        return

    async_add_entities([WWWeatherForecast(ww_data, name, unit)], True)


class WWWeatherForecast(WeatherEntity):
    """Implementation of the WillyWeather weather component."""

    def __init__(self, weather_data, name, unit):
        """Initialize the component."""
        self._name = name
        self._data = weather_data
        self._unit = unit

    @property
    def name(self):
        """Return the name."""
        if self._name == 'WW':
            return self._data.latest_data['location']["name"]
        return self._name

    @property
    def condition(self):
        """Return the weather condition."""
        return MAP_CONDITION.get(self._data.latest_data['forecasts']["weather"]["days"][0]["entries"][0].get("precisCode"))

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

    @property
    def forecast(self):
        """Return the forecast array."""
        try:

            forecast_data = []
            for  num, v in enumerate(self._data.latest_data['forecasts']["weather"]["days"]):
                date_string = datetime.strptime(v['entries'][0]['dateTime'], "%Y-%m-%d %H:%M:%S").strftime("%Y-%m-%dT%H:%M:%S")
                data_dict = {
                    ATTR_FORECAST_TIME: date_string,
                    ATTR_FORECAST_TEMP: v['entries'][0]['max'],
                    ATTR_FORECAST_TEMP_LOW: v['entries'][0]['min'],
                    ATTR_FORECAST_PRECIPITATION: self._data.latest_data['forecasts']["rainfall"]["days"][num]['entries'][0]['endRange'],
                    ATTR_FORECAST_CONDITION: MAP_CONDITION.get(v['entries'][0]['precisCode'])
                }
                forecast_data.append(data_dict)
            return forecast_data

        except (ValueError, IndexError):
            return STATE_UNKNOWN

    async def async_update(self):
        """Get the latest data from WillyWeather and updates the states."""
        await self._data.async_update()
        if not self._data:
            _LOGGER.info("Didn't receive weather data from WillyWeather")
            return

class WeatherData:
    """Handle WillyWeather API object and limit updates."""

    def __init__(self, api_key, station_id, days):
        """Initialize the data object."""
        self._api_key = api_key
        self._station_id = station_id
        self._days = days

    def _build_url(self):
        """Build the URL for the requests."""
        url = _RESOURCE.format(self._api_key, self._station_id, self._days)
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
