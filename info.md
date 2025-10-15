[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/custom-components/hacs) [![willyweather](https://img.shields.io/github/release/safepay/sensor.willyweather.svg)](https://github.com/safepay/sensor.willyweather) ![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)

A custom Home Assistant integration providing comprehensive weather data from WillyWeather Australia.

This differs from the BoM integration by providing separate binary sensors for warnings as well as data that is unavailable such as tide and swell information.

While the WillyWeather API requires a credit card on file, this integration will likely not exceed the 5000 free requests per day.

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
