"""Constants for the WillyWeather integration."""
from homeassistant.const import (
    PERCENTAGE,
    UnitOfPrecipitationDepth,
    UnitOfPressure,
    UnitOfSpeed,
    UnitOfTemperature,
)
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorStateClass,
)

DOMAIN = "willyweather"
ATTRIBUTION = "Data provided by WillyWeather"

CONF_STATION_ID = "station_id"
CONF_API_KEY = "api_key"
CONF_DAYS = "days"

DEFAULT_NAME = "WillyWeather"
DEFAULT_DAYS = 5

API_BASE_URL = "https://api.willyweather.com.au/v2"
API_TIMEOUT = 10

SENSOR_TYPES = {
    'temperature': {
        'name': 'Temperature',
        'unit': UnitOfTemperature.CELSIUS,
        'icon': 'mdi:thermometer',
        'device_class': SensorDeviceClass.TEMPERATURE,
        'state_class': SensorStateClass.MEASUREMENT,
    },
    'apparent_temperature': {
        'name': 'Feels Like',
        'unit': UnitOfTemperature.CELSIUS,
        'icon': 'mdi:thermometer',
        'device_class': SensorDeviceClass.TEMPERATURE,
        'state_class': SensorStateClass.MEASUREMENT,
    },
    'cloud': {
        'name': 'Cloud',
        'unit': 'okta',
        'icon': 'mdi:weather-partlycloudy',
        'device_class': None,
        'state_class': None,
    },
    'humidity': {
        'name': 'Humidity',
        'unit': PERCENTAGE,
        'icon': 'mdi:water-percent',
        'device_class': SensorDeviceClass.HUMIDITY,
        'state_class': SensorStateClass.MEASUREMENT,
    },
    'dewpoint': {
        'name': 'Dew Point',
        'unit': UnitOfTemperature.CELSIUS,
        'icon': 'mdi:thermometer',
        'device_class': SensorDeviceClass.TEMPERATURE,
        'state_class': SensorStateClass.MEASUREMENT,
    },
    'pressure': {
        'name': 'Pressure',
        'unit': UnitOfPressure.HPA,
        'icon': 'mdi:gauge',
        'device_class': SensorDeviceClass.PRESSURE,
        'state_class': SensorStateClass.MEASUREMENT,
    },
    'wind_speed': {
        'name': 'Wind Speed',
        'unit': UnitOfSpeed.KILOMETERS_PER_HOUR,
        'icon': 'mdi:weather-windy',
        'device_class': SensorDeviceClass.WIND_SPEED,
        'state_class': SensorStateClass.MEASUREMENT,
    },
    'wind_gust': {
        'name': 'Wind Gust',
        'unit': UnitOfSpeed.KILOMETERS_PER_HOUR,
        'icon': 'mdi:weather-windy-variant',
        'device_class': SensorDeviceClass.WIND_SPEED,
        'state_class': SensorStateClass.MEASUREMENT,
    },
    'wind_bearing': {
        'name': 'Wind Bearing',
        'unit': '°',
        'icon': 'mdi:compass',
        'device_class': None,
        'state_class': None,
    },
    'wind_direction': {
        'name': 'Wind Direction',
        'unit': None,
        'icon': 'mdi:compass',
        'device_class': None,
        'state_class': None,
    },
    'rainlasthour': {
        'name': 'Rain Last Hour',
        'unit': UnitOfPrecipitationDepth.MILLIMETERS,
        'icon': 'mdi:weather-rainy',
        'device_class': SensorDeviceClass.PRECIPITATION,
        'state_class': SensorStateClass.MEASUREMENT,
    },
    'raintoday': {
        'name': 'Rain Today',
        'unit': UnitOfPrecipitationDepth.MILLIMETERS,
        'icon': 'mdi:weather-rainy',
        'device_class': SensorDeviceClass.PRECIPITATION,
        'state_class': SensorStateClass.TOTAL_INCREASING,
    },
    'rainsince9am': {
        'name': 'Rain Since 9am',
        'unit': UnitOfPrecipitationDepth.MILLIMETERS,
        'icon': 'mdi:weather-rainy',
        'device_class': SensorDeviceClass.PRECIPITATION,
        'state_class': SensorStateClass.TOTAL_INCREASING,
    },
}

FORECAST_TYPES = {
    'forecast_maxtemp': {
        'name': 'Max Temp',
        'unit': UnitOfTemperature.CELSIUS,
        'icon': 'mdi:thermometer',
    },
    'forecast_mintemp': {
        'name': 'Min Temp',
        'unit': UnitOfTemperature.CELSIUS,
        'icon': 'mdi:thermometer',
    },
    'forecast_rain': {
        'name': 'Rain',
        'unit': UnitOfPrecipitationDepth.MILLIMETERS,
        'icon': 'mdi:weather-rainy',
    },
    'forecast_rain_prob': {
        'name': 'Rain Probability',
        'unit': PERCENTAGE,
        'icon': 'mdi:weather-rainy',
    },
    'forecast_summary': {
        'name': 'Summary',
        'unit': '',
        'icon': '',
    },
    'forecast_icon': {
        'name': 'Icon',
        'unit': '',
        'icon': '',
    },
}

MAP_CONDITION = {
    'fine': 'sunny',
    'mostly-fine': 'sunny',
    'high-cloud': 'partlycloudy',
    'partly-cloudy': 'partlycloudy',
    'mostly-cloudy': 'cloudy',
    'cloudy': 'cloudy',
    'overcast': 'cloudy',
    'shower-or-two': 'rainy',
    'chance-shower-fine': 'rainy',
    'chance-shower-cloud': 'rainy',
    'drizzle': 'rainy',
    'few-showers': 'rainy',
    'showers-rain': 'rainy',
    'heavy-showers-rain': 'pouring',
    'chance-thunderstorm-fine': 'lightning',
    'chance-thunderstorm-cloud': 'lightning',
    'chance-thunderstorm-showers': 'lightning-rainy',
    'thunderstorm': 'lightning-rainy',
    'chance-snow-fine': 'snowy',
    'chance-snow-cloud': 'snowy',
    'snow-and-rain': 'snowy-rainy',
    'light-snow': 'snowy',
    'snow': 'snowy',
    'heavy-snow': 'snowy',
    'wind': 'windy',
    'frost': 'clear-night',
    'fog': 'fog',
    'hail': 'hail',
    'dust': 'exceptional',
}

DARK_SKY_ICONS = {
    'fine': 'clear-day',
    'mostly-fine': 'clear-day',
    'high-cloud': 'partly-cloudy-day',
    'partly-cloudy': 'partly-cloudy-day',
    'mostly-cloudy': 'partly-cloudy-day',
    'cloudy': 'partly-cloudy-day',
    'overcast': 'partly-cloudy-day',
    'shower-or-two': 'rain',
    'chance-shower-fine': 'rain',
    'chance-shower-cloud': 'rain',
    'drizzle': 'rain',
    'few-showers': 'rain',
    'showers-rain': 'rain',
    'heavy-showers-rain': 'rain',
    'chance-thunderstorm-fine': 'lightning',
    'chance-thunderstorm-cloud': 'lightning',
    'chance-thunderstorm-showers': 'lightning',
    'thunderstorm': 'thunderstorm',
    'chance-snow-fine': 'snow',
    'chance-snow-cloud': 'snow',
    'snow-and-rain': 'snow',
    'light-snow': 'snow',
    'snow': 'snow',
    'heavy-snow': 'snow',
    'wind': 'wind',
    'frost': 'clear-night',
    'fog': 'fog',
    'hail': 'hail',
    'dust': None,
}
