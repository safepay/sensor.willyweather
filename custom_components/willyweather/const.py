"""Constants for the WillyWeather integration."""
from typing import Final

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
from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
)

DOMAIN: Final = "willyweather"
ATTRIBUTION: Final = "Data provided by WillyWeather"
MANUFACTURER: Final = "WillyWeather"

# Configuration
CONF_STATION_ID: Final = "station_id"
CONF_STATION_NAME: Final = "station_name"
CONF_INCLUDE_OBSERVATIONAL: Final = "include_observational"
CONF_INCLUDE_WARNINGS: Final = "include_warnings"
CONF_ADDITIONAL_FORECAST: Final = "additional_forecast"

# Additional forecast options (checkboxes)
CONF_INCLUDE_UV: Final = "include_uv"
CONF_INCLUDE_TIDES: Final = "include_tides"
CONF_INCLUDE_WIND: Final = "include_wind"

# API
API_BASE_URL: Final = "https://api.willyweather.com.au/v2"
API_TIMEOUT: Final = 10

# Update intervals
UPDATE_INTERVAL_OBSERVATION: Final = 10  # minutes

# Condition mapping
CONDITION_MAP: Final = {
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

# Observational sensor types (created when enabled)
SENSOR_TYPES: Final = {
    "temperature": {
        "name": "Temperature",
        "unit": UnitOfTemperature.CELSIUS,
        "icon": "mdi:thermometer",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "state_class": SensorStateClass.MEASUREMENT,
        "path": ["temperature", "temperature"],
    },
    "apparent_temperature": {
        "name": "Apparent Temperature",
        "unit": UnitOfTemperature.CELSIUS,
        "icon": "mdi:thermometer",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "state_class": SensorStateClass.MEASUREMENT,
        "path": ["temperature", "apparentTemperature"],
    },
    "humidity": {
        "name": "Humidity",
        "unit": PERCENTAGE,
        "icon": "mdi:water-percent",
        "device_class": SensorDeviceClass.HUMIDITY,
        "state_class": SensorStateClass.MEASUREMENT,
        "path": ["humidity", "percentage"],
    },
    "dewpoint": {
        "name": "Dew Point",
        "unit": UnitOfTemperature.CELSIUS,
        "icon": "mdi:thermometer",
        "device_class": SensorDeviceClass.TEMPERATURE,
        "state_class": SensorStateClass.MEASUREMENT,
        "path": ["dewPoint", "temperature"],
    },
    "pressure": {
        "name": "Pressure",
        "unit": UnitOfPressure.HPA,
        "icon": "mdi:gauge",
        "device_class": SensorDeviceClass.PRESSURE,
        "state_class": SensorStateClass.MEASUREMENT,
        "path": ["pressure", "pressure"],
    },
    "wind_speed": {
        "name": "Wind Speed",
        "unit": UnitOfSpeed.KILOMETERS_PER_HOUR,
        "icon": "mdi:weather-windy",
        "device_class": SensorDeviceClass.WIND_SPEED,
        "state_class": SensorStateClass.MEASUREMENT,
        "path": ["wind", "speed"],
    },
    "wind_gust": {
        "name": "Wind Gust",
        "unit": UnitOfSpeed.KILOMETERS_PER_HOUR,
        "icon": "mdi:weather-windy-variant",
        "device_class": SensorDeviceClass.WIND_SPEED,
        "state_class": SensorStateClass.MEASUREMENT,
        "path": ["wind", "gustSpeed"],
    },
    "wind_direction": {
        "name": "Wind Direction",
        "unit": "°",
        "icon": "mdi:compass",
        "device_class": None,
        "state_class": None,
        "path": ["wind", "direction"],
    },
    "wind_direction_text": {
        "name": "Wind Direction Text",
        "unit": None,
        "icon": "mdi:compass",
        "device_class": None,
        "state_class": None,
        "path": ["wind", "directionText"],
    },
    "cloud": {
        "name": "Cloud Cover",
        "unit": "oktas",
        "icon": "mdi:cloud",
        "device_class": None,
        "state_class": SensorStateClass.MEASUREMENT,
        "path": ["cloud", "oktas"],
    },
    "rain_last_hour": {
        "name": "Rain Last Hour",
        "unit": UnitOfPrecipitationDepth.MILLIMETERS,
        "icon": "mdi:weather-rainy",
        "device_class": SensorDeviceClass.PRECIPITATION,
        "state_class": SensorStateClass.MEASUREMENT,
        "path": ["rainfall", "lastHourAmount"],
    },
    "rain_today": {
        "name": "Rain Today",
        "unit": UnitOfPrecipitationDepth.MILLIMETERS,
        "icon": "mdi:weather-rainy",
        "device_class": SensorDeviceClass.PRECIPITATION,
        "state_class": SensorStateClass.TOTAL_INCREASING,
        "path": ["rainfall", "todayAmount"],
    },
    "rain_since_9am": {
        "name": "Rain Since 9am",
        "unit": UnitOfPrecipitationDepth.MILLIMETERS,
        "icon": "mdi:weather-rainy",
        "device_class": SensorDeviceClass.PRECIPITATION,
        "state_class": SensorStateClass.TOTAL_INCREASING,
        "path": ["rainfall", "since9AMAmount"],
    },
}

# Sun/Moon sensor types (if sunrisesunset enabled)
SUNMOON_SENSOR_TYPES: Final = {
    "sunrise": {
        "name": "Sunrise",
        "unit": None,
        "icon": "mdi:weather-sunset-up",
        "device_class": SensorDeviceClass.TIMESTAMP,
    },
    "sunset": {
        "name": "Sunset",
        "unit": None,
        "icon": "mdi:weather-sunset-down",
        "device_class": SensorDeviceClass.TIMESTAMP,
    },
    "moonrise": {
        "name": "Moonrise",
        "unit": None,
        "icon": "mdi:moon-waxing-crescent",
        "device_class": SensorDeviceClass.TIMESTAMP,
    },
    "moonset": {
        "name": "Moonset",
        "unit": None,
        "icon": "mdi:moon-waning-crescent",
        "device_class": SensorDeviceClass.TIMESTAMP,
    },
    "moon_phase": {
        "name": "Moon Phase",
        "unit": None,
        "icon": "mdi:moon-full",
    },
}

# Tide sensor types (if tides enabled)
TIDES_SENSOR_TYPES: Final = {
    "next_high_tide": {
        "name": "Next High Tide",
        "unit": None,
        "icon": "mdi:waves-arrow-up",
        "device_class": SensorDeviceClass.TIMESTAMP,
    },
    "next_low_tide": {
        "name": "Next Low Tide",
        "unit": None,
        "icon": "mdi:waves-arrow-down",
        "device_class": SensorDeviceClass.TIMESTAMP,
    },
    "next_high_tide_height": {
        "name": "Next High Tide Height",
        "unit": "m",
        "icon": "mdi:waves-arrow-up",
    },
    "next_low_tide_height": {
        "name": "Next Low Tide Height",
        "unit": "m",
        "icon": "mdi:waves-arrow-down",
    },
}

# UV sensor types (if UV enabled)
UV_SENSOR_TYPES: Final = {
    "uv_index": {
        "name": "UV Index",
        "unit": None,
        "icon": "mdi:weather-sunny-alert",
    },
    "uv_alert": {
        "name": "UV Alert",
        "unit": None,
        "icon": "mdi:weather-sunny-alert",
    },
}

# Wind forecast sensor types (if wind enabled)
WIND_FORECAST_TYPES: Final = {
    "wind_speed_forecast": {
        "name": "Wind Speed Forecast",
        "unit": UnitOfSpeed.KILOMETERS_PER_HOUR,
        "icon": "mdi:weather-windy",
        "device_class": SensorDeviceClass.WIND_SPEED,
    },
    "wind_direction_forecast": {
        "name": "Wind Direction Forecast",
        "unit": "°",
        "icon": "mdi:compass",
    },
}

# Warning binary sensor types (created when enabled)
WARNING_BINARY_SENSOR_TYPES: Final = {
    "storm_warning": {
        "name": "Storm Warning",
        "icon": "mdi:weather-lightning-rainy",
        "device_class": BinarySensorDeviceClass.SAFETY,
    },
    "flood_warning": {
        "name": "Flood Warning",
        "icon": "mdi:water-alert",
        "device_class": BinarySensorDeviceClass.SAFETY,
    },
    "fire_warning": {
        "name": "Fire Warning",
        "icon": "mdi:fire-alert",
        "device_class": BinarySensorDeviceClass.SAFETY,
    },
    "heat_warning": {
        "name": "Heat Warning",
        "icon": "mdi:thermometer-alert",
        "device_class": BinarySensorDeviceClass.SAFETY,
    },
    "wind_warning": {
        "name": "Wind Warning",
        "icon": "mdi:weather-windy-variant",
        "device_class": BinarySensorDeviceClass.SAFETY,
    },
}