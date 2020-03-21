[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/custom-components/hacs) [![willyweather](https://img.shields.io/github/release/safepay/sensor.willyweather.svg)](https://github.com/safepay/sensor.willyweather) ![Maintenance](https://img.shields.io/maintenance/yes/2020.svg)


# WillyWeather Custom Component for Home Assistant
WillyWeather is an Australian weather service that presents Bureau of Meteorology data in an easy to use interface.
It also provides a Rest API that is easier to use than the cumbersome BoM API's.
https://www.willyweather.com.au/api/docs/v2.html

Note that the service is commercial but it is very cheap.

The main difference with this sensor is that it returns all data regardless of your location.
In some areas of Australia, a single weather station will not provide all data. WillyWeather sources data from multiple local weather stations to give you the best result.

This is also very easy to configure, using your lat and long settings in HA, and creates minimal HA overhead due to RESTful API.

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

![WillyWeather Example Config](https://github.com/safepay/sensor.willyweather/raw/master/willyweather_api_config.png)

Complete the process with your own information, including your credit card.

### Location Selection
The location is determined from the closest station based on the lat/long in Home Assistant.
This can be over-written by station_id in the config

## Sensor
The willyweather sensor provides observational data for the closest weather station.

To add WillyWeather sensors to your installation, add the desired lines from the following example to your configuration.yaml file:

### Example configuration.yaml entry
```yaml
sensor:
  - platform: willyweather
    api_key: your_api_key
```
### CONFIGURATION VARIABLES
key | required | type | default | description
--- | -------- | ---- | ------- | -----------
`api_key` | yes | string | | The API Key for your account at the WillyWeather website.
`station_id` | no | string | closest | The station ID as identified from the WillyWeather website.
`name` | no | string | `WW` | The name you would like to give to the weather station.
`forecast_days` | no | int | None | Generate additional sensors for each forecast day which can then be used in other components such as the DarkSky Weather Card.
`monitored_conditions` | no | list | all | A list of the conditions to monitor from: `temperature`, `apparent_temperature`, `cloud`, `humidity`, `dewpoint`, `pressure`, `wind_speed`, `wind_gust`, `wind_direction`, `rainlasthour`, `raintoday`, `rainsince9am`

### DarkSky Weather Card

These sensors support the [DarkSky Weather Card](https://github.com/iammexx/home-assistant-config/tree/master/ui/darksky)

Add:
```yaml
    forecast_days: 7
```
to your config, then follow the DarkSky README.

To get the card working use:
```
type: 'custom:dark-sky-weather-card'
entity_current_conditions: sensor.ww_day_0_icon
entity_current_text: sensor.ww_day_0_summary
entity_forecast_high_temp_1: sensor.ww_day_1_max_temp
entity_forecast_high_temp_2: sensor.ww_day_2_max_temp
entity_forecast_high_temp_3: sensor.ww_day_3_max_temp
entity_forecast_high_temp_4: sensor.ww_day_4_max_temp
entity_forecast_high_temp_5: sensor.ww_day_5_max_temp
entity_forecast_icon_1: sensor.ww_day_0_icon
entity_forecast_icon_2: sensor.ww_day_1_icon
entity_forecast_icon_3: sensor.ww_day_2_icon
entity_forecast_icon_4: sensor.ww_day_3_icon
entity_forecast_icon_5: sensor.ww_day_4_icon
entity_forecast_low_temp_1: sensor.ww_day_0_min_temp
entity_forecast_low_temp_2: sensor.ww_day_1_min_temp
entity_forecast_low_temp_3: sensor.ww_day_2_min_temp
entity_forecast_low_temp_4: sensor.ww_day_3_min_temp
entity_forecast_low_temp_5: sensor.ww_day_4_min_temp
entity_summary_1: sensor.ww_day_0_summary
entity_summary_2: sensor.ww_day_1_summary
entity_summary_3: sensor.ww_day_2_summary
entity_summary_4: sensor.ww_day_3_summary
entity_summary_5: sensor.ww_day_4_summary
entity_temperature: sensor.ww_temperature
entity_sun: sun.sun
entity_daytime_high: sensor.ww_day_0_max_temp
entity_wind_bearing: sensor.ww_wind_direction
entity_wind_speed: sensor.ww_wind_speed
entity_humidity: sensor.ww_humidity
entity_pressure: sensor.ww_pressure
entity_apparent_temp: sensor.ww_feels_like
entity_pop: sensor.ww_day_0_rain_probability
entity_pop_1: sensor.ww_day_1_rain_probability
entity_pop_2: sensor.ww_day_2_rain_probability
entity_pop_3: sensor.ww_day_3_rain_probability
entity_pop_4: sensor.ww_day_4_rain_probability
entity_pop_5: sensor.ww_day_5_rain_probability
```

## Weather

The willyweather weather component provides observational data and a four day forecast for the closest weather station.

To add WillyWeather sensors to your installation, add the desired lines from the following example to your configuration.yaml file:

### Example configuration.yaml entry
```yaml
weather:
  - platform: willyweather
    api_key: your_api_key
```
### CONFIGURATION VARIABLES
key | required | type | default | description
--- | -------- | ---- | ------- | -----------
`api_key` | yes | string | | The API Key for your account at the WillyWeather website.
`station_id` | no | string | closest | The station ID as identified from the WillyWeather website.
`name` | no | string | closest | The name you would like to give to the weather station.
