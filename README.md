# Home-Assistant Custom Modules

## WillyWeather
WillyWeather is an Australian weather service that presents Bureau of Meteorology data is an easy to use interface.
It also provides a Rest API that is easier to use than the cumbersome BoM API's.

Install the directory and all files within a custom_componenets directory within your Home Assistant config directory.

You must obtain an API key from your WillyWeather account at www.willyweather.com.au.

## Register for the Willyweather API
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
