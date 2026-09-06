from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant.components import websocket_api
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.event import async_track_time_change
from homeassistant.helpers.service import async_extract_config_entry_ids

from .api import OpenTDBClient
from .const import (
    CONF_REFRESH_TIME,
    DOMAIN,
    PLATFORMS,
    SERVICE_ANSWER,
    SERVICE_NEW,
    SERVICE_NEXT,
    SERVICE_REFRESH,
    SERVICE_REFRESH_QUESTIONS,
    SERVICE_RESET,
    SERVICE_START,
)
from .coordinator import QuizDataUpdateCoordinator
from .loader import async_ensure_questions_dir

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass: HomeAssistant, config: dict[str, Any]) -> bool:
    hass.data.setdefault(DOMAIN, {})
    await async_ensure_questions_dir(hass)
    _register_services(hass)
    _register_websocket_commands(hass)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    api = OpenTDBClient(async_get_clientsession(hass))
    coordinator = QuizDataUpdateCoordinator(hass, entry, api)
    await coordinator.async_load_stored()
    if not coordinator.has_questions:
        await coordinator.async_daily_refresh()
    coordinator.async_set_updated_data(coordinator._build_view(None))
    hass.data[DOMAIN][entry.entry_id] = coordinator
    registry = er.async_get(hass)
    retired_sensor_suffixes = {"question", "score", "elapsed_time", "player_statistics"}
    for entity in er.async_entries_for_config_entry(registry, entry.entry_id):
        if entity.domain == "sensor" and any(
            entity.unique_id.endswith(f"_{suffix}") for suffix in retired_sensor_suffixes
        ):
            registry.async_remove(entity.entity_id)

    async def _options_updated(hass: HomeAssistant, updated_entry: ConfigEntry) -> None:
        await coordinator.async_reset_quiz_for_all()

    entry.async_on_unload(entry.add_update_listener(_options_updated))
    refresh = entry.options.get(CONF_REFRESH_TIME, entry.data.get(CONF_REFRESH_TIME, "00:00:00"))
    hour, minute, second = (int(value) for value in refresh.split(":"))
    entry.async_on_unload(
        async_track_time_change(
            hass,
            lambda _now: hass.async_create_task(coordinator.async_daily_refresh()),
            hour=hour,
            minute=minute,
            second=second,
        )
    )
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unloaded = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unloaded:
        hass.data[DOMAIN].pop(entry.entry_id, None)
    return unloaded


def _register_services(hass: HomeAssistant) -> None:
    if hass.services.has_service(DOMAIN, SERVICE_START):
        return

    async def get_coordinators(call: ServiceCall) -> list[QuizDataUpdateCoordinator]:
        ids = await async_extract_config_entry_ids(hass, call)
        coordinators = hass.data[DOMAIN]
        return [coordinators[entry_id] for entry_id in ids if entry_id in coordinators]

    async def require_user(call: ServiceCall) -> str:
        if not call.context.user_id:
            raise ValueError("An authenticated Home Assistant user is required")
        return call.context.user_id

    async def player_name(user_id: str) -> str:
        user = await hass.auth.async_get_user(user_id)
        return user.name if user and user.name else "Player"

    async def start(call: ServiceCall) -> None:
        user_id = await require_user(call)
        name = await player_name(user_id)
        for coordinator in await get_coordinators(call):
            coordinator.set_player_name(user_id, name)
            await coordinator.async_start_quiz(user_id)

    async def new_quiz(call: ServiceCall) -> None:
        user_id = await require_user(call)
        name = await player_name(user_id)
        for coordinator in await get_coordinators(call):
            coordinator.set_player_name(user_id, name)
            await coordinator.async_start_quiz(user_id, force_new=True)

    async def answer(call: ServiceCall) -> None:
        user_id = await require_user(call)
        name = await player_name(user_id)
        for coordinator in await get_coordinators(call):
            coordinator.set_player_name(user_id, name)
            await coordinator.async_answer_question(
                user_id, int(call.data["question_index"]), call.data["answer"]
            )

    async def next_question(call: ServiceCall) -> None:
        user_id = await require_user(call)
        for coordinator in await get_coordinators(call):
            await coordinator.async_next_question(user_id)

    async def reset(call: ServiceCall) -> None:
        user_id = await require_user(call)
        for coordinator in await get_coordinators(call):
            await coordinator.async_reset_quiz(user_id)

    async def refresh(call: ServiceCall) -> None:
        for coordinator in await get_coordinators(call):
            await coordinator.async_refresh()

    hass.services.async_register(DOMAIN, SERVICE_START, start)
    hass.services.async_register(DOMAIN, SERVICE_NEW, new_quiz)
    hass.services.async_register(DOMAIN, SERVICE_ANSWER, answer)
    hass.services.async_register(DOMAIN, SERVICE_NEXT, next_question)
    hass.services.async_register(DOMAIN, SERVICE_RESET, reset)
    hass.services.async_register(DOMAIN, SERVICE_REFRESH, refresh)
    hass.services.async_register(DOMAIN, SERVICE_REFRESH_QUESTIONS, new_quiz)


def _register_websocket_commands(hass: HomeAssistant) -> None:
    """Register card commands that return only the caller's quiz state."""

    def get_coordinator(quiz_id: str) -> QuizDataUpdateCoordinator:
        entity = er.async_get(hass).async_get(quiz_id)
        if (
            entity is None
            or entity.config_entry_id not in hass.data[DOMAIN]
            or entity.unique_id != f"{entity.config_entry_id}_quiz"
        ):
            raise ValueError("The selected OpenTDB quiz is unavailable")
        return hass.data[DOMAIN][entity.config_entry_id]

    async def player_name(user_id: str) -> str:
        user = await hass.auth.async_get_user(user_id)
        return user.name if user and user.name else "Player"

    async def run_command(
        connection: websocket_api.ActiveConnection,
        msg: dict[str, Any],
        action: str,
    ) -> None:
        try:
            coordinator = get_coordinator(msg["quiz_id"])
            user_id = connection.user.id
            coordinator.set_player_name(user_id, await player_name(user_id))
            if action == "start":
                await coordinator.async_start_quiz(user_id)
            elif action == "new":
                await coordinator.async_start_quiz(user_id, force_new=True)
            else:
                coordinator.validate_session(user_id, msg["session_id"])
                if action == "submit":
                    await coordinator.async_answer_question(
                        user_id, msg["question_index"], msg["answer"]
                    )
                else:
                    await coordinator.async_next_question(user_id)
            connection.send_result(msg["id"], coordinator._build_view(user_id))
        except ValueError as err:
            connection.send_error(msg["id"], "invalid_request", str(err))
        except Exception:
            _LOGGER.exception("OpenTDB WebSocket command failed")
            connection.send_error(msg["id"], "unknown_error", "Unable to update quiz session")

    @websocket_api.websocket_command(
        {vol.Required("type"): "opentdb/session/start", vol.Required("quiz_id"): str}
    )
    @websocket_api.async_response
    async def websocket_start(
        hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
    ) -> None:
        await run_command(connection, msg, "start")

    @websocket_api.websocket_command(
        {vol.Required("type"): "opentdb/session/new", vol.Required("quiz_id"): str}
    )
    @websocket_api.async_response
    async def websocket_new(
        hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
    ) -> None:
        await run_command(connection, msg, "new")

    @websocket_api.websocket_command(
        {
            vol.Required("type"): "opentdb/session/submit",
            vol.Required("quiz_id"): str,
            vol.Required("session_id"): str,
            vol.Required("question_index"): int,
            vol.Required("answer"): str,
        }
    )
    @websocket_api.async_response
    async def websocket_submit(
        hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
    ) -> None:
        await run_command(connection, msg, "submit")

    @websocket_api.websocket_command(
        {
            vol.Required("type"): "opentdb/session/next",
            vol.Required("quiz_id"): str,
            vol.Required("session_id"): str,
        }
    )
    @websocket_api.async_response
    async def websocket_next(
        hass: HomeAssistant, connection: websocket_api.ActiveConnection, msg: dict[str, Any]
    ) -> None:
        await run_command(connection, msg, "next")

    websocket_api.async_register_command(hass, websocket_start)
    websocket_api.async_register_command(hass, websocket_new)
    websocket_api.async_register_command(hass, websocket_submit)
    websocket_api.async_register_command(hass, websocket_next)
