"""Platform for sensor integration."""
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
):
    """Set up the sensor platform."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    sensors = []
    for price_type in ["current", "next"]:
        sensors.append(
            ElektrarnaSensor(
                coordinator, price_type, "priceEur", "EUR/MWh", "mdi:currency-eur"
            )
        )
        sensors.append(
            ElektrarnaSensor(
                coordinator, price_type, "priceCzk", "CZK/MWh", "mdi:cash-100"
            )
        )
        sensors.append(
            ElektrarnaSensor(
                coordinator, price_type, "priceCzkVat", "CZK/MWh", "mdi:cash-100"
            )
        )
        sensors.append(
            ElektrarnaSensor(
                coordinator, price_type, "priceCzkKwh", "CZK/kWh", "mdi:cash-100"
            )
        )
        sensors.append(
            ElektrarnaSensor(
                coordinator, price_type, "exchRateCzkEur", "CZK/EUR", "mdi:currency-eur",
            )
        )
        sensors.append(
            ElektrarnaSensor(
                coordinator, price_type, "priceLevel", None, "mdi:chart-line"
            )
        )

    async_add_entities(sensors)


class ElektrarnaSensor(CoordinatorEntity, Entity):
    """Representation of a Sensor."""

    def __init__(self, coordinator, price_type, key, unit, icon):
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._price_type = price_type
        self._key = key
        self._unit = unit
        self._icon = icon
        self._attr_device_info = {
            "identifiers": {(DOMAIN, "elektrarna_api")},
            "name": "Elektrárna",
            "manufacturer": "HostMania.eu",
        }

    @property
    def name(self):
        """Return the name of the sensor."""
        return f"Elektrarna-{self._price_type}-{self._key}"

    @property
    def state(self):
        """Return the state of the sensor."""
        if self.coordinator.data and self.coordinator.data.get(self._price_type):
            return self.coordinator.data[self._price_type].get(self._key)
        return None

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._unit

    @property
    def icon(self):
        """Return the icon of the sensor."""
        return self._icon

    @property
    def unique_id(self):
        """Return a unique ID."""
        return f"elektrarna_{self._price_type}_{self._key}"
