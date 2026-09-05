from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector
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


def _schema(categories: list[dict[str, Any]], defaults: dict[str, Any] | None = None) -> vol.Schema:
    values = defaults or {}
    category_options = [
        {"value": "", "label": "Any category"},
        *[
            {"value": str(category["id"]), "label": str(category["name"])}
            for category in sorted(
                (category for category in categories if "id" in category and "name" in category),
                key=lambda category: str(category["name"]).casefold(),
            )
        ],
    ]
    return vol.Schema(
        {
            vol.Required(CONF_QUIZ_NAME, default=values.get(CONF_QUIZ_NAME, "Trivia Quiz")): str,
            vol.Required(CONF_AMOUNT, default=values.get(CONF_AMOUNT, DEFAULT_AMOUNT)): vol.All(
                vol.Coerce(int), vol.Range(min=MIN_AMOUNT, max=MAX_AMOUNT)
            ),
            vol.Required(
                CONF_CATEGORY, default=values.get(CONF_CATEGORY, "")
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=category_options, mode=selector.SelectSelectorMode.DROPDOWN
                )
            ),
            vol.Required(
                CONF_DIFFICULTY, default=values.get(CONF_DIFFICULTY, "")
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=[
                        {"value": "", "label": "Any difficulty"},
                        {"value": "easy", "label": "Easy"},
                        {"value": "medium", "label": "Medium"},
                        {"value": "hard", "label": "Hard"},
                    ],
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            ),
            vol.Required(CONF_TYPE, default=values.get(CONF_TYPE, "")): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=[
                        {"value": "", "label": "Any question type"},
                        {"value": "multiple", "label": "Multiple choice"},
                        {"value": "boolean", "label": "True / False"},
                    ],
                    mode=selector.SelectSelectorMode.DROPDOWN,
                )
            ),
            vol.Required(
                CONF_REFRESH_TIME, default=values.get(CONF_REFRESH_TIME, DEFAULT_REFRESH_TIME)
            ): str,
        }
    )


class OpenTDBConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> Any:
        errors: dict[str, str] = {}
        client = OpenTDBClient(async_get_clientsession(self.hass))
        try:
            categories = await client.async_get_categories()
        except OpenTDBError:
            categories = []
            errors["base"] = "cannot_connect"
        if user_input:
            try:
                await client.async_fetch_questions(
                    user_input[CONF_AMOUNT],
                    user_input.get(CONF_CATEGORY),
                    user_input.get(CONF_DIFFICULTY),
                    user_input.get(CONF_TYPE),
                )
            except OpenTDBError:
                errors["base"] = "cannot_connect"
            else:
                await self.async_set_unique_id(
                    f"{DOMAIN}_{user_input[CONF_QUIZ_NAME].strip().lower().replace(' ', '_')}"
                )
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title=user_input[CONF_QUIZ_NAME], data=user_input)
        return self.async_show_form(
            step_id="user", data_schema=_schema(categories, user_input), errors=errors
        )

    class OptionsFlowHandler(config_entries.OptionsFlow):
        async def async_step_init(self, user_input: dict[str, Any] | None = None) -> Any:
            if user_input:
                return self.async_create_entry(title="", data=user_input)
            defaults = {**self.config_entry.data, **self.config_entry.options}
            client = OpenTDBClient(async_get_clientsession(self.hass))
            try:
                categories = await client.async_get_categories()
            except OpenTDBError:
                categories = []
            return self.async_show_form(step_id="init", data_schema=_schema(categories, defaults))

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry) -> OptionsFlowHandler:
        return OpenTDBConfigFlow.OptionsFlowHandler()
