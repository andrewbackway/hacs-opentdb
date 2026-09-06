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
    CONF_FILE,
    CONF_QUIZ_NAME,
    CONF_REFRESH_TIME,
    CONF_SOURCE,
    CONF_TYPE,
    DEFAULT_AMOUNT,
    DEFAULT_REFRESH_TIME,
    DOMAIN,
    MAX_AMOUNT,
    MIN_AMOUNT,
    SOURCE_FILE,
    SOURCE_OPENTDB,
)
from .loader import (
    QuestionFileError,
    async_list_question_files,
    async_load_question_file,
)


def _opentdb_schema(categories: list[dict[str, Any]], defaults: dict[str, Any] | None = None) -> vol.Schema:
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


def _file_schema(files: list[str], defaults: dict[str, Any] | None = None) -> vol.Schema:
    values = defaults or {}
    current = values.get(CONF_FILE)
    options = [{"value": name, "label": name} for name in files]
    if current and current not in files:
        options.append({"value": current, "label": f"{current} (missing)"})
    return vol.Schema(
        {
            vol.Required(CONF_QUIZ_NAME, default=values.get(CONF_QUIZ_NAME, "Trivia Quiz")): str,
            vol.Required(
                CONF_FILE, default=current or (files[0] if files else "")
            ): selector.SelectSelector(
                selector.SelectSelectorConfig(
                    options=options, mode=selector.SelectSelectorMode.DROPDOWN
                )
            ),
            vol.Required(CONF_AMOUNT, default=values.get(CONF_AMOUNT, DEFAULT_AMOUNT)): vol.All(
                vol.Coerce(int), vol.Range(min=MIN_AMOUNT, max=MAX_AMOUNT)
            ),
            vol.Required(
                CONF_REFRESH_TIME, default=values.get(CONF_REFRESH_TIME, DEFAULT_REFRESH_TIME)
            ): str,
        }
    )


class OpenTDBConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> Any:
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")
        return self.async_show_menu(step_id="user", menu_options=[SOURCE_OPENTDB, SOURCE_FILE])

    async def async_step_opentdb(self, user_input: dict[str, Any] | None = None) -> Any:
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
                return await self._create_entry({**user_input, CONF_SOURCE: SOURCE_OPENTDB})
        return self.async_show_form(
            step_id="opentdb", data_schema=_opentdb_schema(categories, user_input), errors=errors
        )

    async def async_step_file(self, user_input: dict[str, Any] | None = None) -> Any:
        errors: dict[str, str] = {}
        files = await async_list_question_files(self.hass)
        if not files:
            return self.async_abort(reason="no_question_files")
        if user_input:
            try:
                await async_load_question_file(self.hass, user_input[CONF_FILE])
            except QuestionFileError:
                errors["base"] = "invalid_file"
            else:
                return await self._create_entry({**user_input, CONF_SOURCE: SOURCE_FILE})
        return self.async_show_form(
            step_id="file", data_schema=_file_schema(files, user_input), errors=errors
        )

    async def _create_entry(self, data: dict[str, Any]) -> Any:
        await self.async_set_unique_id(
            f"{DOMAIN}_{data[CONF_QUIZ_NAME].strip().lower().replace(' ', '_')}"
        )
        self._abort_if_unique_id_configured()
        return self.async_create_entry(title=data[CONF_QUIZ_NAME], data=data)

    class OptionsFlowHandler(config_entries.OptionsFlow):
        async def async_step_init(self, user_input: dict[str, Any] | None = None) -> Any:
            if user_input is not None:
                return self.async_create_entry(title="", data=user_input)
            defaults = {**self.config_entry.data, **self.config_entry.options}
            if defaults.get(CONF_SOURCE) == SOURCE_FILE:
                files = await async_list_question_files(self.hass)
                return self.async_show_form(
                    step_id="init", data_schema=_file_schema(files, defaults)
                )
            client = OpenTDBClient(async_get_clientsession(self.hass))
            try:
                categories = await client.async_get_categories()
            except OpenTDBError:
                categories = []
            return self.async_show_form(
                step_id="init", data_schema=_opentdb_schema(categories, defaults)
            )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry) -> OptionsFlowHandler:
        return OpenTDBConfigFlow.OptionsFlowHandler()
