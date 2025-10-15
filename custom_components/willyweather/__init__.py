"""The WillyWeather integration."""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from homeassistant.const import CONF_API_KEY, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.device_registry import async_get as async_get_device_registry
from homeassistant.helpers.entity_registry import async_get as async_get_entity_registry

from .const import CONF_STATION_ID, CONF_STATION_NAME, DOMAIN, MANUFACTURER
from .coordinator import WillyWeatherDataUpdateCoordinator

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.SENSOR, Platform.WEATHER, Platform.BINARY_SENSOR]

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up WillyWeather from a config entry."""
    coordinator = WillyWeatherDataUpdateCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Create main parent device
    station_id = entry.data.get(CONF_STATION_ID)
    station_name = entry.data.get(CONF_STATION_NAME, f"Station {station_id}")
    
    device_registry = async_get_device_registry(hass)
    device_registry.async_get_or_create(
        config_entry_id=entry.entry_id,
        identifiers={(DOMAIN, station_id)},
        manufacturer=MANUFACTURER,
        name=station_name,
    )

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register update listener for options changes
    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        coordinator = hass.data[DOMAIN].pop(entry.entry_id)
        await coordinator.async_shutdown()

    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry when options change."""
    # Clean up entities that are no longer enabled
    await async_cleanup_disabled_entities(hass, entry)
    
    await hass.config_entries.async_reload(entry.entry_id)


async def async_cleanup_disabled_entities(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Remove entities for disabled sensor types."""
    entity_registry = async_get_entity_registry(hass)
    station_id = entry.data.get(CONF_STATION_ID)
    
    # Get all entities for this config entry
    entities = [
        entity
        for entity in entity_registry.entities.values()
        if entity.config_entry_id == entry.entry_id
    ]
    
    # Import sensor type definitions
    from .const import (
        CONF_INCLUDE_OBSERVATIONAL,
        CONF_INCLUDE_SWELL,
        CONF_INCLUDE_TIDES,
        CONF_INCLUDE_UV,
        CONF_INCLUDE_WARNINGS,
        CONF_INCLUDE_WIND,
        SENSOR_TYPES,
        SWELL_SENSOR_TYPES,
        SUNMOON_SENSOR_TYPES,
        TIDES_SENSOR_TYPES,
        UV_SENSOR_TYPES,
        WARNING_BINARY_SENSOR_TYPES,
        WIND_FORECAST_TYPES,
    )
    
    # Build list of entity unique_ids that should be removed
    entities_to_remove = []
    
    # Check observational sensors
    if not entry.options.get(CONF_INCLUDE_OBSERVATIONAL, True):
        for sensor_type in SENSOR_TYPES:
            entities_to_remove.append(f"{station_id}_{sensor_type}")
        for sensor_type in SUNMOON_SENSOR_TYPES:
            entities_to_remove.append(f"{station_id}_{sensor_type}")
    
    # Check swell sensors
    if not entry.options.get(CONF_INCLUDE_SWELL, False):
        for sensor_type in SWELL_SENSOR_TYPES:
            entities_to_remove.append(f"{station_id}_{sensor_type}")
    
    # Check tide sensors
    if not entry.options.get(CONF_INCLUDE_TIDES, False):
        for sensor_type in TIDES_SENSOR_TYPES:
            entities_to_remove.append(f"{station_id}_{sensor_type}")
    
    # Check UV sensors
    if not entry.options.get(CONF_INCLUDE_UV, True):
        for sensor_type in UV_SENSOR_TYPES:
            entities_to_remove.append(f"{station_id}_{sensor_type}")
    
    # Check wind forecast sensors
    if not entry.options.get(CONF_INCLUDE_WIND, True):
        for sensor_type in WIND_FORECAST_TYPES:
            entities_to_remove.append(f"{station_id}_{sensor_type}")
    
    # Check warning sensors
    if not entry.options.get(CONF_INCLUDE_WARNINGS, True):
        for sensor_type in WARNING_BINARY_SENSOR_TYPES:
            entities_to_remove.append(f"{station_id}_{sensor_type}")
    
    # Remove the entities
    for entity in entities:
        if entity.unique_id in entities_to_remove:
            _LOGGER.info("Removing disabled entity: %s", entity.entity_id)
            entity_registry.async_remove(entity.entity_id)