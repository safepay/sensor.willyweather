[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/custom-components/hacs) [![willyweather](https://img.shields.io/github/release/safepay/sensor.willyweather.svg)](https://github.com/safepay/sensor.willyweather) ![Maintenance](https://img.shields.io/maintenance/yes/2020.svg)

## An Australian BoM alternative using WillyWeather

www.willyweather.com.au provide a cheap API that is more usable than the BoM API.

The advantage is that they source data for your location from the closest weather stations, rather than you choosing a specific weather station.

This is much better if you are in a rural area and the closest weather station does not provide all data.

### Setup
You will need to obtain an API key from https://www.willyweather.com.au/account/api.html

Full instructions in the README.md

### Configuration
```
sensor:
  - platform: willyweather
    api_key: your_api_key

```
