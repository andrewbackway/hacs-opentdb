from __future__ import annotations

from datetime import time
from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.config_entries import ConfigFlowResult
from homeassistant.const import CONF_TIME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api import OpenTDBClient, OpenTDBError
from .const import (
    CONF_AMOUNT,
    CONF_CATEGORY,
    CONF_DIFFICULTY,
    CONF_QUIZ_NAME,
    CONF_REFRESH_TIME,
    CONF_TYPE,
    DEFAULT_AMOUNT,
    DEFAULT_REFRESH_TIME,
    DOMAIN,
    MAX_AMOUNT,
    MIN_AMOUNT,
)


def _schema(defaults: dict[str, Any] | None = None) -> vol.Schema:
    values = defaults or {}
    return vol.Schema(
        {
            vol.Required(CONF_QUIZ_NAME, default=values.get(CONF_QUIZ_NAME, "Trivia Quiz")): str,
            vol.Required(CONF_AMOUNT, default=values.get(CONF_AMOUNT, DEFAULT_AMOUNT)): vol.All(vol.Coerce(int), vol.Range(min=MIN_AMOUNT, max=MAX_AMOUNT)),
            vol.Optional(CONF_CATEGORY, default=values.get(CONF_CATEGORY, "")): str,
            vol.Optional(CONF_DIFFICULTY, default=values.get(CONF_DIFFICULTY, "")): vol.In(["", "easy", "medium", "hard"]),
            vol.Optional(CONF_TYPE, default=values.get(CONF_TYPE, "")): vol.In(["", "multiple", "boolean"]),
            vol.Required(CONF_REFRESH_TIME, default=values.get(CONF_REFRESH_TIME, DEFAULT_REFRESH_TIME)): str,
        }
    )


class OpenTDBConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input:
            try:
                client = OpenTDBClient(async_get_clientsession(self.hass))
                await client.async_fetch_questions(
                    user_input[CONF_AMOUNT], user_input.get(CONF_CATEGORY), user_input.get(CONF_DIFFICULTY), user_input.get(CONF_TYPE)
                )
            except OpenTDBError:
                errors["base"] = "cannot_connect"
            else:
                await self.async_set_unique_id(f"{DOMAIN}_{user_input[CONF_QUIZ_NAME].strip().lower().replace(' ', '_')}")
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title=user_input[CONF_QUIZ_NAME], data=user_input)
        return self.async_show_form(step_id="user", data_schema=_schema(user_input), errors=errors)

    @staticmethod
    @config_entries.options_flow
    class OptionsFlowHandler(config_entries.OptionsFlow):
        async def async_step_init(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
            if user_input:
                return self.async_create_entry(title="", data=user_input)
            defaults = {**self.config_entry.data, **self.config_entry.options}
            return self.async_show_form(step_id="init", data_schema=_schema(defaults))

    @staticmethod
    def async_get_options_flow(config_entry: config_entries.ConfigEntry) -> OptionsFlowHandler:
        return OpenTDBConfigFlow.OptionsFlowHandler()
