"""The Elektrárna integration."""
import asyncio
import logging
from datetime import timedelta

import async_timeout
import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor"]
CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

async def async_setup(hass: HomeAssistant, config: dict):
    """Set up the Elektrárna component."""
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Elektrárna from a config entry."""
    hass.data.setdefault(DOMAIN, {})

    coordinator = ElektrarnaDataUpdateCoordinator(hass)
    await coordinator.async_config_entry_first_refresh()

    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


class ElektrarnaDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the API."""

    def __init__(self, hass):
        """Initialize."""
        self._hass = hass
        self.api = ElektrarnaApi(hass)

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(minutes=1),
        )

    async def _async_update_data(self):
        """Update data via library."""
        try:
            async with async_timeout.timeout(10):
                (
                    current,
                    next_p,
                    cheapest,
                    cheapest_34h,
                ) = await asyncio.gather(
                    self.api.get_current_price(),
                    self.api.get_next_price(),
                    self.api.get_cheapest_intervals(),
                    self.api.get_cheapest_intervals_34h(),
                )
                return {
                    "current": current,
                    "next": next_p,
                    "cheapest_intervals": cheapest,
                    "cheapest_intervals_34h": cheapest_34h,
                }
        except Exception as exception:
            raise UpdateFailed(f"Error communicating with API: {exception}")


class ElektrarnaApi:
    """An API client for Elektrárna."""

    def __init__(self, hass):
        """Initialize."""
        self._hass = hass

    async def get_current_price(self):
        """Get the current price."""
        session = async_get_clientsession(self._hass)
        async with session.get(
            "https://elektrarna-api.hostmania.eu/api/v1/currentprice"
        ) as response:
            response.raise_for_status()
            return await response.json()

    async def get_next_price(self):
        """Get the next price."""
        session = async_get_clientsession(self._hass)
        async with session.get(
            "https://elektrarna-api.hostmania.eu/api/v1/nextprice"
        ) as response:
            response.raise_for_status()
            return await response.json()

    async def get_cheapest_intervals(self):
        """Get the cheapest intervals."""
        session = async_get_clientsession(self._hass)
        async with session.get(
            "https://elektrarna-api.hostmania.eu/api/v1/cheapest-intervals/today"
        ) as response:
            response.raise_for_status()
            return await response.json()

    async def get_cheapest_intervals_34h(self):
        """Get the cheapest intervals for today and tomorrow (10+24 hours)."""
        session = async_get_clientsession(self._hass)
        async with session.get(
            "https://elektrarna-api.hostmania.eu/api/v1/cheapest-intervals/today34h"
        ) as response:
            if response.status == 404:
                _LOGGER.info("No data available for 34h cheapest intervals yet (data for tomorrow are not available)")
                return {}
            response.raise_for_status()
            return await response.json()
