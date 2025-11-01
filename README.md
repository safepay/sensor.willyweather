# WillyWeather Integration for Home Assistant
[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/custom-components/hacs) [![willyweather](https://img.shields.io/github/release/safepay/sensor.willyweather.svg)](https://github.com/safepay/sensor.willyweather) ![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)

A custom Home Assistant integration providing comprehensive weather data from WillyWeather Australia.

This differs from the BoM integration by providing separate binary sensors for warnings as well as data that is unavailable such as tide and swell information.

## Features

- **Weather Entity**: Real-time weather conditions with full daily and hourly forecast support
- **Observational Sensors**: Current weather measurements including temperature, humidity, pressure, wind, rainfall, and more
- **Sun/Moon Data**: Sunrise, sunset, moonrise, moonset, and moon phase information with dynamic moon phase icons
- **Tide Information**: Next high and low tide times and heights (coastal locations)
- **UV Index**: Current UV levels with alert categories
- **Swell Data**: Wave height, period, and direction (coastal locations)
- **Wind Forecasts**: Detailed wind speed and direction forecasts
- **Weather Warnings**: Binary sensors for active weather warnings
- **Automatic Station Detection**: Automatically finds the closest WillyWeather station based on your Home Assistant location
- **Configurable Data**: Enable/disable optional sensors through the UI
- **Forecast Data**: Daily (7 days) and hourly (3 days) with comprehensive data points

## Installation

### HACS (Recommended, but not yet available!)
1. Add this repository as a custom repository in HACS
2. Search for "WillyWeather" in HACS
3. Click **Install**
4. Restart Home Assistant

### Manual Installation
1. Copy the `custom_components/willyweather` folder to your Home Assistant's `custom_components` directory
2. Restart Home Assistant

### Through the UI
1. Go to **Settings** → **Devices & Services**
2. Click **Add Integration** button
3. Search for "WillyWeather"
4. Follow the setup wizard:
   - **Step 1**: Enter your WillyWeather API key (optional: specify a station ID, or leave blank for auto-detection)
   - **Step 2**: Select which sensors to include
   - **Step 3**: Select to include binary warning sensors

## Configuration

### Getting an API Key
You need a WillyWeather API key to use this integration:

1. Visit https://www.willyweather.com.au/info/api.html
2. Sign up for a free API account
3. Copy your API key to use during setup
4. Tick single location, weather (observation and forecasts) and warnings
5. Swell and tide sections are optional if your station does not support those features

![WillyWeather API Config](https://github.com/safepay/sensor.willyweather/blob/master/willyweather_api_config.png?raw=true)

### Available Configuration Options

When setting up, you can configure:

- **Include observational sensors** - Enables current weather measurement sensors (default: Yes)
- **Include wind forecast data** - Includes wind speed and direction forecasts (default: Yes)
- **Include UV index sensors** - Includes UV index and alert levels (default: Yes)
- **Include tide information** - Includes tide times and heights for coastal locations (default: No)
- **Include swell data** - Includes wave height, period, and direction for coastal locations (default: No)
- **Include warning sensors** - Enables binary sensors for weather warnings (default: Yes)

These options match the [WillyWeather API configuration screen](https://www.willyweather.com.au/api/docs/weather.html) settings, allowing you to select only the data types your location requires.

## Entities

### Weather Entity
A single weather entity provides:
- Current conditions and temperature (actual and apparent)
- Humidity, pressure, and wind speed/direction/gusts
- Cloud coverage and dew point
- Daily forecasts (7 days)
- Hourly forecasts (3 days)

The forecasts include extended data when optional sensors are enabled:
- **Daily forecasts**: UV index, sunrise/sunset, moon phase, tide times/heights, rainfall probability
- **Hourly forecasts**: UV index, wind data, rainfall probability, swell data

Access forecasts using the `weather.get_forecasts` service:
```yaml
service: weather.get_forecasts
data:
  type: daily
target:
  entity_id: weather.willyweather_
```

### Observational Sensors (Current Conditions)
When observational sensors are enabled, the following sensors are created:

#### Temperature & Humidity
- **Temperature** - Current air temperature in °C
- **Apparent Temperature** - "Feels like" temperature in °C
- **Delta-T** - Delta-T temperature in °C (difference between air temperature and wet bulb temperature, used in agricultural spraying and fire danger calculations)
- **Humidity** - Relative humidity percentage
- **Dew Point** - Dew point temperature in °C
 
#### Pressure & Cloud
- **Pressure** - Atmospheric pressure in hPa
- **Cloud Cover** - Cloud coverage in oktas (0-8)

#### Wind
- **Wind Speed** - Current wind speed in km/h
- **Wind Gust** - Wind gust speed in km/h
- **Wind Direction** - Wind direction in degrees
- **Wind Direction Text** - Wind direction as compass point (N, NE, E, etc.)

#### Rainfall
- **Rain Last Hour** - Rainfall in the last hour in mm
- **Rain Today** - Total rainfall today in mm
- **Rain Since 9am** - Rainfall since 9am in mm

### Sun & Moon Sensors
Always included with observational sensors:

- **Sunrise** - Next sunrise time
- **Sunset** - Next sunset time
- **Moonrise** - Next moonrise time
- **Moonset** - Next moonset time
- **Moon Phase** - Current moon phase (New Moon, Waxing Crescent, First Quarter, Waxing Gibbous, Full Moon, Waning Gibbous, Last Quarter, Waning Crescent) with dynamic icon

### Tide Sensors (Optional - Coastal Locations)
When tide sensors are enabled:

- **Next High Tide** - Time of next high tide
- **Next High Tide Height** - Height of next high tide in meters
- **Next Low Tide** - Time of next low tide
- **Next Low Tide Height** - Height of next low tide in meters

*Note: Not all locations have tidal data. Sensors will show as unavailable if no data exists for your location.*

### UV Sensors (Optional)
When UV sensors are enabled:

- **UV Index** - Current UV index value
- **UV Alert** - UV alert level (Low, Moderate, High, Very High, Extreme)

### Wind Forecast Sensors (Optional)
When wind forecast sensors are enabled:

- **Wind Speed Forecast** - Forecasted wind speed in km/h
- **Wind Direction Forecast** - Forecasted wind direction in degrees

### Swell Sensors (Optional - Coastal Locations)
When swell sensors are enabled:

- **Swell Height** - Current swell height in meters
- **Swell Period** - Swell period in seconds
- **Swell Direction** - Swell direction in degrees
- **Swell Direction Text** - Swell direction as compass point

*Note: Not all locations have swell data. Sensors will show as unavailable if no data exists for your location.*

### Weather Warning Binary Sensors (Optional)
When warning sensors are enabled, binary sensors are created for each warning type. These sensors turn "on" when a warning is active and include severity information as attributes.

Available warning types:
- **Storm Warning**
- **Flood Warning**
- **Fire Warning**
- **Heat Warning**
- **Wind Warning**
- **Weather Warning**
- **Strong Wind Warning**
- **Thunderstorm Warning**
- **Frost Warning**
- **Rain Warning**
- **Snow Warning**
- **Hail Warning**
- **Cyclone Warning**
- **Tsunami Warning**
- **Fog Warning**

#### Warning Attributes
Each active warning sensor includes the following attributes:

- **severity** - Warning severity level: `yellow` (minor), `amber` (moderate), or `red` (severe)
- **warning_count** - Number of active warnings for this type
- **warnings** - List of active warnings with details:
  - `code` - Official warning code
  - `name` - Warning name
  - `issue_time` - When the warning was issued
  - `expire_time` - When the warning expires
  - `severity` - Individual warning severity
  - `warning_type` - Type of warning

#### Example Automation Using Warning Severity
```yaml
automation:
  - alias: "Severe Weather Alert"
    trigger:
      - platform: state
        entity_id: binary_sensor.storm_warning
        to: "on"
    condition:
      - condition: template
        value_template: "{{ state_attr('binary_sensor.storm_warning', 'severity') == 'red' }}"
    action:
      - service: notify.mobile_app
        data:
          message: >
            SEVERE STORM WARNING! 
            {{ state_attr('binary_sensor.storm_warning', 'warning_count') }} warning(s) active.
          title: "⚠️ Weather Alert"
```

## Devices

The integration creates multiple device groupings to organize entities:

- **Main Station Device** - Parent device for the weather entity
- **Sensors Device** - Groups all observational, sun/moon, tide, UV, wind, and swell sensors
- **Binary Sensors Device** - Groups all warning binary sensors

## Troubleshooting

### No Data for Tides/Swell
Not all WillyWeather locations provide tide or swell data. If sensors show as "unavailable", this is expected for inland locations. Check the WillyWeather website to confirm if your location supports these data types.

### Station Auto-Detection
If automatic station detection fails:
1. Visit https://www.willyweather.com.au
2. Search for your location
3. Note the station ID from the page source. Look for `ww.location`.
4. Manually enter this ID during setup

### API Rate Limits
The free WillyWeather API has rate limits. The integration updates every 10 minutes by default.

### Warnings Not Showing
Warning sensors only appear when warnings are active in your area. During periods without active warnings, the sensors will show as "off" with no attributes.

## Support

For issues, feature requests, or questions:
- [GitHub Issues](https://github.com/safepay/sensor.willyweather/issues)
- [Home Assistant Community Forum](https://community.home-assistant.io/)

## Credits

This integration uses the [WillyWeather API](https://www.willyweather.com.au/info/api.html).

## License

This project is licensed under the MIT License.
