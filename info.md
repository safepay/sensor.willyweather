[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/custom-components/hacs) [![willyweather](https://img.shields.io/github/release/safepay/sensor.willyweather.svg)](https://github.com/safepay/sensor.willyweather) ![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)

A custom Home Assistant integration providing comprehensive weather data from WillyWeather Australia.

This differs from the BoM integration by providing separate binary sensors for warnings as well as data that is unavailable such as tide and swell information.

## Features

- **Weather Entity**: Real-time weather conditions with full daily and hourly forecast support
- **Observational Sensors**: Current weather measurements including temperature, humidity, pressure, wind, rainfall, and more
- **Sun/Moon Data**: Sunrise, sunset, moonrise, moonset, and moon phase information with dynamic moon phase icons
- **Tide Information**: High and low tide times and heights (Coastal locations. Also available in daily forecast data)
- **Swell Information**: Wave heights, periods and directions (Coastal locations. Also available in hourly forecast data)
- **Weather Warnings**: Binary sensors for active storm, flood, fire, heat, wind, frost warnings and more
- **Automatic Station Detection**: Automatically finds the closest WillyWeather station based on your Home Assistant location
- **Configurable Data**: Enable/disable optional sensors through the UI
- **Configurable Update Intervals**: Set different update frequencies for day and night to manage API usage
- **Forecast Data**: Daily (7 days) and hourly (3 days) with comprehensive data points

## API Usage Management

The integration includes configurable day/night update intervals to help manage API usage:
- Default: 10-minute updates during the day, 30-minute updates at night
- Fully customizable through the UI (5-60 minutes day, 10-120 minutes night)
- Automatically switches between day and night modes
- Each update makes 2-3 API calls depending on configuration
- Typical usage with defaults: ~10,000 calls/month

Configure update intervals during setup or anytime through **Settings** → **Devices & Services** → **WillyWeather** → **Configure**.
