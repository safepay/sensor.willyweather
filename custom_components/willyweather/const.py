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

DOMAIN: Final = "willyweather"
ATTRIBUTION: Final = "Data provided by WillyWeather"
MANUFACTURER: Final = "WillyWeather"

# Configuration
CONF_STATION_ID: Final = "station_id"
CONF_STATION_NAME: Final = "station_name"
CONF_FORECAST_DAYS: Final = "forecast_days"
CONF_SENSOR_FORMAT: Final = "sensor_format"

# Forecast options
CONF_FORECAST_RAINFALL: Final = "forecast_rainfall"
CONF_FORECAST_SUNRISESUNSET: Final = "forecast_sunrisesunset"
CONF_FORECAST_TIDES: Final = "forecast_tides"
CONF_FORECAST_UV: Final = "forecast_uv"

# Sensor format options
SENSOR_FORMAT_DARKSKY: Final = "darksky"
SENSOR_FORMAT_BOM: Final = "bom"

DEFAULT_FORECAST_DAYS: Final = 5

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

# Observational sensor types (always created)
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

# Dark Sky format forecast sensor types
DARKSKY_FORECAST_TYPES: Final = {
    "forecast_icon": {
        "name": "Icon",
        "unit": None,
        "icon": "mdi:weather-partly-cloudy",
    },
    "forecast_summary": {
        "name": "Summary",
        "unit": None,
        "icon": "mdi:text",
    },
    "forecast_temp_high": {
        "name": "Daytime High Temperature",
        "unit": UnitOfTemperature.CELSIUS,
        "icon": "mdi:thermometer",
        "device_class": SensorDeviceClass.TEMPERATURE,
    },
    "forecast_temp_low": {
        "name": "Overnight Low Temperature",
        "unit": UnitOfTemperature.CELSIUS,
        "icon": "mdi:thermometer",
        "device_class": SensorDeviceClass.TEMPERATURE,
    },
}

# Dark Sky format rainfall sensors (if rainfall enabled)
DARKSKY_RAINFALL_TYPES: Final = {
    "forecast_precip": {
        "name": "Precipitation",
        "unit": UnitOfPrecipitationDepth.MILLIMETERS,
        "icon": "mdi:weather-rainy",
        "device_class": SensorDeviceClass.PRECIPITATION,
    },
    "forecast_precip_probability": {
        "name": "Precipitation Probability",
        "unit": PERCENTAGE,
        "icon": "mdi:weather-rainy",
    },
}

# Dark Sky format UV sensors (if UV enabled)
DARKSKY_UV_TYPES: Final = {
    "forecast_uv_index": {
        "name": "UV Index",
        "unit": None,
        "icon": "mdi:weather-sunny-alert",
    },
}

# BoM format forecast sensor types
BOM_FORECAST_TYPES: Final = {
    "icon_descriptor": {
        "name": "Icon Descriptor",
        "unit": None,
        "icon": "mdi:weather-partly-cloudy",
    },
    "short_text": {
        "name": "Short Text",
        "unit": None,
        "icon": "mdi:text",
    },
    "temp_max": {
        "name": "Max Temp",
        "unit": UnitOfTemperature.CELSIUS,
        "icon": "mdi:thermometer",
        "device_class": SensorDeviceClass.TEMPERATURE,
    },
    "temp_min": {
        "name": "Min Temp",
        "unit": UnitOfTemperature.CELSIUS,
        "icon": "mdi:thermometer",
        "device_class": SensorDeviceClass.TEMPERATURE,
    },
}

# BoM format rainfall sensors (if rainfall enabled)
BOM_RAINFALL_TYPES: Final = {
    "rain_amount_min": {
        "name": "Rain Amount Min",
        "unit": UnitOfPrecipitationDepth.MILLIMETERS,
        "icon": "mdi:weather-rainy",
        "device_class": SensorDeviceClass.PRECIPITATION,
    },
    "rain_amount_max": {
        "name": "Rain Amount Max",
        "unit": UnitOfPrecipitationDepth.MILLIMETERS,
        "icon": "mdi:weather-rainy",
        "device_class": SensorDeviceClass.PRECIPITATION,
    },
    "rain_amount_range": {
        "name": "Rain Amount Range",
        "unit": UnitOfPrecipitationDepth.MILLIMETERS,
        "icon": "mdi:weather-rainy",
        "device_class": SensorDeviceClass.PRECIPITATION,
    },
    "rain_chance": {
        "name": "Rain Chance",
        "unit": PERCENTAGE,
        "icon": "mdi:weather-rainy",
    },
}

# BoM format UV sensors (if UV enabled)
BOM_UV_TYPES: Final = {
    "uv_alert": {
        "name": "UV Alert",
        "unit": None,
        "icon": "mdi:weather-sunny-alert",
    },
    "uv_category": {
        "name": "UV Category",
        "unit": None,
        "icon": "mdi:weather-sunny-alert",
    },
    "uv_max_index": {
        "name": "UV Max Index",
        "unit": None,
        "icon": "mdi:weather-sunny-alert",
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