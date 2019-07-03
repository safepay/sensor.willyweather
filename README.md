# WillyWeather Custom Module for Home Assistant
WillyWeather is an Australian weather service that presents Bureau of Meteorology data is an easy to use interface.
It also provides a Rest API that is easier to use than the cumbersome BoM API's.
https://www.willyweather.com.au/api/docs/v2.html

## Installation
Install the directory and all files within a custom_componenets directory within your Home Assistant config directory.
You must obtain an API key from your WillyWeather account at www.willyweather.com.au.

## Register for the WillyWeather API
Go to https://www.willyweather.com.au/info/api.html.

Select "Single Location" and click "Next".

Select "Show sub-items" next to "Weather" to reveal the sub-menu.

Tick "Observational".

## Location Selection
The location is determined from the closest station based on the lat/long in Home Assistant.
This can be over-written by station_id in the config

## Sensor
The willyweather sensor provides observational data for the closest weather station.

To add WillyWeather sensors to your installation, add the desired lines from the following example to your configuration.yaml file:

## Example configuration.yaml entry
```
sensor:
  - platform: willyweather
    api_key: your_api_key
```
## CONFIGURATION VARIABLES

### station_id
(string)(Optional) The station ID string as identified from the WillyWeather website.

Default value: If not given, defaults to the closest station based on location data in Home Assistant.

### name
(string)(Optional) The name you would like to give to the weather station.

### monitored_conditions
(list)(Optional) A list of the conditions to monitor.
Default value: If not given, defaults to all conditions listed below.

#### temperature
Temperature in C
#### apparent_temperature
Temperature in C
#### cloud
Cloud in Oktas
#### humidity
Humidity in %
#### dewpoint
Temperature in C
#### pressure
Pressure in hPa
#### wind_speed
Wind speed in km/h
#### wind_gust
Wind gust in km/h
#### wind_direction
Wind direction
#### rainlasthour
Rain last hour in mm
#### raintoday
Rain today in mm
#### rainsince9am
Rain since 9am in mm
