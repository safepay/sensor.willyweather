[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/custom-components/hacs) [![willyweather](https://img.shields.io/github/release/safepay/sensor.willyweather.svg)](https://github.com/safepay/sensor.willyweather)


# WillyWeather Custom Component for Home Assistant
WillyWeather is an Australian weather service that presents Bureau of Meteorology data is an easy to use interface.
It also provides a Rest API that is easier to use than the cumbersome BoM API's.
https://www.willyweather.com.au/api/docs/v2.html

Note that the service is commercial but it is very cheap.

The main difference with this sensor is that it returns all data regardless of your location.
In some areas of Australia, a single weather station will not provide all data. WillyWeather sources data from multiple local weather stations to give you the best result.

This is also very easy to configure, using your lat and long settings in HA.

## Installation
Install the directory and all files within a custom_componenets directory within your Home Assistant config directory.
You must obtain an API key from your WillyWeather account at www.willyweather.com.au.

### Register for the WillyWeather API
Go to https://www.willyweather.com.au/info/api.html.

Select "Single Location" and click "Next".

Select "Show sub-items" next to "Weather" to reveal the sub-menu.

Tick "Observational".

Select "Show sub-items" next to "Forecasts" to reveal the sub-menu.

Tick "Weather" and "Rainfall" and click "Next".

Complete the process with your own information, including your credit card.

### Location Selection
The location is determined from the closest station based on the lat/long in Home Assistant.
This can be over-written by station_id in the config

## Sensor
The willyweather sensor provides observational data for the closest weather station.

To add WillyWeather sensors to your installation, add the desired lines from the following example to your configuration.yaml file:

### Example configuration.yaml entry
```
sensor:
  - platform: willyweather
    api_key: your_api_key
```
### CONFIGURATION VARIABLES
key | required | type | default | description
--- | -------- | ---- | ------- | -----------
``api_key`` | yes | string | | The api_key for your account at the WillyWeather website.
``station_id`` | no | string | closest | The station ID as identified from the WillyWeather website.
``name`` | no | string | closest | The name you would like to give to the weather station.
``monitored_conditions`` | no | list | all | A list of the conditions to monitor from: ``temperature, apparent_temperature, cloud, humidity, dewpoint, pressure, wind_speed, wind_gust, wind_direction, rainlasthour, raintoday, rainsince9am``

## Weather

The willyweather weather component provides observational data and a four day forecast for the closest weather station.

To add WillyWeather sensors to your installation, add the desired lines from the following example to your configuration.yaml file:

### Example configuration.yaml entry
```
weather:
  - platform: willyweather
    api_key: your_api_key
```
### CONFIGURATION VARIABLES
key | required | type | default | description
--- | -------- | ---- | ------- | -----------
``api_key`` | yes | string | | The api_key for your account at the WillyWeather website.
``station_id`` | no | string | closest | The station ID as identified from the WillyWeather website.
``name`` | no | string | closest | The name you would like to give to the weather station.
