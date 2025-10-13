[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/custom-components/hacs) [![willyweather](https://img.shields.io/github/release/safepay/sensor.willyweather.svg)](https://github.com/safepay/sensor.willyweather) ![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)


# WillyWeather Integration for Home Assistant

This custom integration provides weather data from WillyWeather Australia to Home Assistant.

## Features

- **Weather Entity**: Real-time weather conditions with daily forecast support via the `weather.get_forecasts` service
- **Observational Sensors**: Temperature, humidity, pressure, wind speed, rainfall, UV index, and more
- **Automatic Station Detection**: Finds the closest WillyWeather station based on your Home Assistant location
- **Configurable**: Enable/disable individual sensors through the UI

## Installation

### HACS (Recommended)

1. Add this repository as a custom repository in HACS
2. Search for "WillyWeather" in HACS
3. Click Install
4. Restart Home Assistant

### Manual Installation

1. Copy the `custom_components/willyweather` folder to your Home Assistant's `custom_components` directory
2. Restart Home Assistant

## Configuration

### Through the UI (Recommended)

1. Go to **Settings** → **Devices & Services**
2. Click **Add Integration**
3. Search for "WillyWeather"
4. Enter your WillyWeather API key
5. (Optional) Enter a specific station ID, or leave blank to auto-detect the closest station

### API Key

You need a WillyWeather API key to use this integration. Get your API key from:
https://www.willyweather.com.au/info/api.html

## Entities

### Weather Entity

The integration creates a weather entity that provides:
- Current conditions
- Temperature (actual and apparent)
- Humidity
- Pressure
- Wind speed and direction
- Daily forecasts (accessed via `weather.get_forecasts` service)

### Sensors

The following sensors are available (can be disabled in options):

**Temperature & Humidity**
- Temperature
- Feels Like (Apparent Temperature)
- Humidity
- Dew Point

**Wind**
- Wind Speed
- Wind Gust
- Wind Direction (degrees)
- Wind Direction (text)

**Precipitation**
- Rain Last Hour
- Rain Today
- Rain Since 9am

**Other**
- Pressure
- Cloud Cover
- UV Index

## Using Forecasts

Home Assistant 2024.3+ uses a service-based approach for weather forecasts. To get forecast data:
```yaml
service: weather.get_forecasts
data:
  type: daily
target:
  entity_id: weather.willyweather_<your_station>
