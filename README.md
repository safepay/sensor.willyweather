# WillyWeather Integration for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/custom-components/hacs) [![willyweather](https://img.shields.io/github/release/safepay/sensor.willyweather.svg)](https://github.com/safepay/sensor.willyweather) ![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)

A custom Home Assistant integration providing comprehensive weather data from WillyWeather Australia.

This differs from the BoM integration by providing separate binary sensors for warnings as well as data that is unavailable such as tide and swell information.

## Features

- **Weather Entity**: Real-time weather conditions with full daily forecast support
- **Observational Sensors**: Current weather measurements including temperature, humidity, pressure, wind, rainfall, and more
- **Sun/Moon Data**: Sunrise, sunset, moonrise, moonset, and moon phase information
- **Tide Information**: High and low tide times and heights (Coastal locations. Also available in daily forecast data)
- **Swell Information**: Times, heights and periods (Coastal locations. Also available in hourly forecast data)
- **Weather Warnings**: Binary sensors for active storm, flood, fire, heat, wind, frost warnings and more
- **Warning Severity**: Binary sensors have an attribute for warning severity - yellow, amber, red
- **Automatic Station Detection**: Automatically finds the closest WillyWeather station based on your Home Assistant location
- **Configurable Data**: Enable/disable optional sensors through the UI
- **Forecast Data**: Daily (7 days) and hourly (3 days)

## Installation

### HACS (Recommended)

1. Add this repository as a custom repository in HACS
2. Search for "WillyWeather" in HACS
3. Click **Install**
4. Restart Home Assistant

### Manual Installation

1. Copy the `custom_components/willyweather` folder to your Home Assistant's `custom_components` directory
2. Restart Home Assistant

## Configuration

### Through the UI

1. Go to **Settings** → **Devices & Services**
2. Click **Create Automation** button
3. Search for "WillyWeather"
4. Follow the setup wizard:
   - **Step 1**: Enter your WillyWeather API key (optional: specify a station ID, or leave blank for auto-detection)
   - **Step 2**: Select which sensors and data types to include
5. For full support, select single location, weather (observation and forecasts) and warnings.

### Getting an API Key

You need a WillyWeather API key to use this integration:

1. Visit https://www.willyweather.com.au/info/api.html
2. Sign up for a free API account
3. Copy your API key to use during setup

### Available Configuration Options

When setting up, you can configure:

- **Include observational sensors** - Enables current weather measurement sensors (default: Yes)
- **Include warning sensors** - Enables binary sensors for severe weather warnings (default: No)
- **Add UV data** - Includes UV index forecasts (default: No)
- **Add tides data** - Includes tide information for coastal locations (default: No)
- **Add wind data** - Includes additional wind forecast data (default: No)
- **Add swell data** - Includes additional swell forecast data (default: No)

These options match the [WillyWeather API configuration screen](https://www.willyweather.com.au/api/docs/weather.html) settings, allowing you to select only the data types your location requires.

## Entities

### Weather Entity

A single weather entity provides:

- Current conditions and temperature (actual and apparent)
- Humidity, pressure, and wind speed/direction
- Cloud coverage and dew point
- Daily forecasts (7 days available)
- Hourly forecasts (3 days available)

Access forecasts using the `weather.get_forecasts` service:
```yaml
service: weather.get_forecasts
data:
  type: daily
target:
  entity_id: weather.willyweather_<station_name>
