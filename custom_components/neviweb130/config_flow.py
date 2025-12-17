"""Config flow for Neviweb130 integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_PASSWORD, CONF_SCAN_INTERVAL, CONF_USERNAME
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from . import LOGIN_URL
from .const import (
    CONF_HOMEKIT_MODE,
    CONF_IGNORE_MIWI,
    CONF_NETWORK,
    CONF_NETWORK2,
    CONF_NETWORK3,
    CONF_NOTIFY,
    CONF_STAT_INTERVAL,
    DOMAIN,
)
from .schema import HOMEKIT_MODE, IGNORE_MIWI, NOTIFY, SCAN_INTERVAL, STAT_INTERVAL


class NeviwebConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Neviweb130."""

    VERSION = 1

    async def _async_validate_credentials(self, user_input: dict[str, Any]) -> dict[str, str]:
        """Validate credentials against the Neviweb service."""

        session = async_get_clientsession(self.hass)
        async with session.post(
            LOGIN_URL,
            json={
                "email": user_input[CONF_USERNAME],
                "password": user_input[CONF_PASSWORD],
            },
        ) as response:
            data = await response.json()

        if response.status != 200 or data.get("error") is not None:
            error_code = data.get("error", {}).get("code") if isinstance(data, dict) else None
            if error_code in ("LOGIN_007", "LOGIN_000", "LOGIN_008"):
                return {"base": "invalid_auth"}
            return {"base": "cannot_connect"}

        return {}

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle the initial step."""

        errors: dict[str, str] = {}

        if user_input is not None:
            await self.async_set_unique_id(user_input[CONF_USERNAME])
            self._abort_if_unique_id_configured()
            errors = await self._async_validate_credentials(user_input)

            if not errors:
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

    async def async_step_options(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle the options flow entrypoint."""

        return await self._show_options_form(user_input)

    async def _show_options_form(self, user_input: dict[str, Any] | None) -> FlowResult:
        if user_input is not None:
            return self.async_create_entry(title="Options", data=user_input)

        entry = self.hass.config_entries.async_get_entry(self.context["entry_id"])
        current = {**(entry.data if entry else {}), **(entry.options if entry else {})}

        current_scan = current.get(CONF_SCAN_INTERVAL, SCAN_INTERVAL)
        if hasattr(current_scan, "total_seconds"):
            current_scan = int(current_scan.total_seconds())

        options_schema = vol.Schema(
            {
                vol.Optional(
                    CONF_SCAN_INTERVAL, default=current_scan
                ): vol.All(vol.Coerce(int)),
                vol.Optional(
                    CONF_HOMEKIT_MODE, default=current.get(CONF_HOMEKIT_MODE, HOMEKIT_MODE)
                ): bool,
                vol.Optional(
                    CONF_IGNORE_MIWI, default=current.get(CONF_IGNORE_MIWI, IGNORE_MIWI)
                ): bool,
                vol.Optional(
                    CONF_STAT_INTERVAL, default=current.get(CONF_STAT_INTERVAL, STAT_INTERVAL)
                ): vol.All(vol.Coerce(int)),
                vol.Optional(CONF_NOTIFY, default=current.get(CONF_NOTIFY, NOTIFY)): vol.In(
                    ["both", "logging", "nothing", "notification"]
                ),
                vol.Optional(CONF_NETWORK, default=current.get(CONF_NETWORK, "")): str,
                vol.Optional(CONF_NETWORK2, default=current.get(CONF_NETWORK2, "")): str,
                vol.Optional(CONF_NETWORK3, default=current.get(CONF_NETWORK3, "")): str,
            }
        )

        return self.async_show_form(step_id="options", data_schema=options_schema)


class NeviwebOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle Neviweb130 options flow."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options for the custom component."""
        flow = NeviwebConfigFlow()
        flow.hass = self.hass
        flow.context = {"entry_id": self.config_entry.entry_id}
        return await flow._show_options_form(user_input)


async def async_get_options_flow(config_entry: config_entries.ConfigEntry):
    """Get the options flow handler."""

    return NeviwebOptionsFlowHandler(config_entry)
