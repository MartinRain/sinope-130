"""Config flow for Neviweb130 integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD, CONF_USERNAME
from homeassistant.data_entry_flow import FlowResult

from .const import CONF_NETWORK, CONF_NETWORK2, CONF_NETWORK3, DOMAIN


class NeviwebConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Neviweb130."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle the initial step."""

        errors: dict[str, str] = {}

        if user_input is not None:
            await self.async_set_unique_id(user_input[CONF_USERNAME])
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title=user_input[CONF_USERNAME], data=user_input)

        data_schema = vol.Schema(
            {
                vol.Required(CONF_USERNAME): str,
                vol.Required(CONF_PASSWORD): str,
                vol.Optional(CONF_NETWORK): str,
                vol.Optional(CONF_NETWORK2): str,
                vol.Optional(CONF_NETWORK3): str,
            }
        )

        return self.async_show_form(step_id="user", data_schema=data_schema, errors=errors)
