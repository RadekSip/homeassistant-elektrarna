"""Config flow for Elektrárna integration."""
import logging
from typing import Any, Dict, Optional

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class ElektrarnaConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Elektrárna."""

    VERSION = 1

    async def async_step_user(
        self, user_input: Optional[Dict[str, Any]] = None
    ) -> FlowResult:
        """Handle the initial step."""
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")

        if user_input is not None:
            return self.async_create_entry(title="Elektrárna", data=user_input)

        return self.async_show_form(step_id="user")
