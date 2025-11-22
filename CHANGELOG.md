# Changelog

All notable changes to the WillyWeather Home Assistant integration will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.2.0] - 2025-01-22

### Added
- **Today's Forecast Sensor**: New observational sensor showing today's short forecast text
  - Displays concise forecast (e.g., "Rainy", "Cloudy")
  - Always available with observational sensors
- **Optional Extended Forecast Text**: Detailed forecast text as sensor attribute
  - Opt-in feature (disabled by default to minimize API usage)
  - Adds detailed narrative forecast (e.g., "Cloudy. High chance of showers, most likely later this evening...")
  - Appears as `extended_forecast` attribute on Today's Forecast sensor
  - Requires 'Region Precis' enabled in WillyWeather API admin
  - **Important**: Adds one extra API call per forecast update when enabled
- **Platinum Weather Card Optimization**: Forecast sensors now optimized for popular weather cards
  - Reordered sensor types to prioritize essential data
  - Default sensors: icon, short forecast, temps (min/max), rain probability, rain amount range
  - Sensor order in config flow matches typical card requirements

### Changed
- **Default Forecast Days**: Reduced from 7 to 5 days
  - Most WillyWeather data is only reliable for 5 days
  - Maximum still configurable up to 7 days
- **Forecast Sensor Defaults**: Changed from "all sensors" to Platinum Weather Card essentials
  - Users can still select all available sensors
  - Better out-of-the-box experience for custom weather cards
- **API Call Optimization**: Extended forecast text now optional instead of always-on
  - Reduces API usage for users who don't need detailed forecast text
  - Clear documentation about cost implications

### Fixed
- **Region Precis API Call**: Fixed x-payload header format for multi-day fetching
  - Changed from POST to GET with properly serialized JSON header
  - Now correctly retrieves extended forecast text for multiple days
- **Forecast Sensor Type Parsing**: Improved data extraction from WillyWeather API
  - Fixed temperature, precis, and icon parsing from weather forecast entries
  - Fixed UV alert parsing from alert.maxIndex and alert.scale

### Improved
- **User Documentation**: Enhanced config flow descriptions
  - Clear warnings about extra API calls and costs
  - Proper terminology matching WillyWeather API admin page ('Region Precis')
  - Explanations of where extended forecast text appears
- **Code Quality**: Removed debug logging from production code
  - Cleaned up temporary warning messages from config_flow.py
  - Production-ready code with appropriate logging levels

## [2.1.0] - 2025-01-20

### Added
- **Customizable Forecast Sensors**: Individual sensors for each forecast day
  - Select which sensor types to create (temperature, rain, UV, etc.)
  - Choose number of forecast days (1-7, default: 5)
  - Perfect for custom Lovelace cards
  - Compatible with BOM Australia integration patterns
- **Forecast Sensor Types**: Multiple data points per forecast day
  - Temperature (min/max)
  - Rain amount (min/max/range)
  - Rain probability
  - Short forecast (precis text)
  - Icon
  - UV index and alert
  - Sunrise/sunset times

### Changed
- **Config Flow Enhancement**: Added multi-step forecast sensor configuration
  - Dedicated step for selecting forecast sensors
  - NumberSelector slider for choosing forecast days
  - List selection for choosing sensor types
  - No additional API calls required (uses existing forecast data)

### Fixed
- **Config Flow State Handling**: Fixed state persistence issues during setup
  - Resolved "unknown error" during integration setup
  - Fixed SelectSelector DROPDOWN mode compatibility issues
  - Improved error handling throughout config flow steps

## [2.0.0] - 2025-01-18

### Added
- **Separate Update Intervals**: Independent control for observational and forecast data
  - Observational data: configurable day/night intervals (default: 10/30 min)
  - Forecast data: configurable day/night intervals (default: 30/60 min)
  - Automatic day/night switching based on configured hours
  - ~21% reduction in API usage vs single interval
- **Day/Night Scheduling**: Configurable hours for day vs night intervals
  - Default night mode: 9 PM to 7 AM
  - Allows slower updates during sleeping hours
  - Separate intervals for observational and forecast data
- **API Usage Optimization**: Smart caching and interval management
  - Forecast data cached between update cycles
  - Only fetches forecast when interval elapsed
  - Always fetches fresh observational data
  - Reduces monthly API calls from ~10,080 to ~7,920 with defaults

### Changed
- **Update Interval Defaults**: New optimized defaults
  - Observational day: 10 minutes (was: 10 minutes)
  - Observational night: 30 minutes (new)
  - Forecast day: 30 minutes (new)
  - Forecast night: 60 minutes (new)
- **Configuration UI**: Enhanced update interval configuration
  - Separate sections for observational and forecast intervals
  - Clear explanations of day/night scheduling
  - API usage calculator in documentation

### Fixed
- **Station Search Timeout**: Increased timeout for station detection
  - Improved reliability during initial setup
  - Better error handling for slow network connections
- **HTTP 400 Errors**: Fixed API request formatting
  - Proper parameter encoding for forecast requests
  - Correct header formatting for all API endpoints

### Improved
- **Documentation**: Comprehensive update interval documentation
  - Usage examples with monthly API call calculations
  - Optimization tips for different usage patterns
  - Clear explanation of day/night scheduling behavior
- **Config Flow**: Multi-step wizard with better organization
  - Step 1: API key and station selection
  - Step 2: Observational sensors
  - Step 3: Forecast options
  - Step 4: Warning sensors
  - Step 5: Forecast sensor selection (if enabled)
  - Step 6: Update intervals

## [1.x.x] - Previous Versions

For changes prior to version 2.0.0, please see the git commit history.

---

## Upgrade Notes

### Upgrading to 2.2.0
- Extended forecast text is now **opt-in** (disabled by default)
  - If you want detailed forecast text, enable "Include extended forecast text" in config
  - Requires 'Region Precis' enabled in WillyWeather API admin
  - Adds one extra API call per forecast update
- Forecast sensor defaults changed to Platinum Weather Card essentials
  - Existing installations keep current sensor selections
  - New installations get optimized defaults
- Default forecast days reduced from 7 to 5
  - Existing installations unchanged
  - New installations default to 5 days

### Upgrading to 2.1.0
- Forecast sensors are now configurable
  - Existing forecast sensors remain unchanged
  - Reconfigure to customize which sensors and days you want

### Upgrading to 2.0.0
- Update intervals are now separated into observational and forecast
  - Existing single interval migrated to both intervals
  - Reconfigure to optimize API usage with separate intervals
- Config flow now has 6 steps instead of 3
  - All existing config preserved during upgrade
  - Reconfigure to access new interval settings

## API Usage Guide

### Typical Monthly Usage (2.2.0 defaults)

**With observational sensors only (extended forecast disabled):**
- Observational: ~3,360 calls/month
- Warnings (if enabled): ~3,360 calls/month
- **Total: ~6,720 calls/month**

**With observational + extended forecast enabled:**
- Observational: ~3,360 calls/month
- Forecast: ~1,200 calls/month
- Extended forecast: ~1,200 calls/month
- Warnings (if enabled): ~3,360 calls/month
- **Total: ~9,120 calls/month**

**With all features enabled (forecast sensors + extended text):**
- Observational: ~3,360 calls/month
- Forecast: ~1,200 calls/month
- Extended forecast: ~1,200 calls/month
- Warnings (if enabled): ~3,360 calls/month
- **Total: ~9,120 calls/month**

### Cost-Saving Tips
1. Disable extended forecast text if you don't need detailed narrative (default)
2. Increase night intervals significantly (e.g., 60-240 min for forecast)
3. Disable warnings if not needed in your area
4. Use minimal forecast days (1-3 instead of 5-7)
5. Increase observational night interval (e.g., 60+ min)
