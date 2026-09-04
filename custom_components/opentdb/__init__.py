from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
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
    SERVICE_RESET,
    SERVICE_START,
)
from .coordinator import QuizDataUpdateCoordinator

async def async_setup(hass: HomeAssistant, config: dict[str, Any]) -> bool:
    hass.data.setdefault(DOMAIN, {})
    _register_services(hass)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    api = OpenTDBClient(async_get_clientsession(hass))
    coordinator = QuizDataUpdateCoordinator(hass, entry, api)
    await coordinator.async_load_stored()
    coordinator.async_set_updated_data(coordinator._build_view(None))
    hass.data[DOMAIN][entry.entry_id] = coordinator

    async def _options_updated(hass: HomeAssistant, updated_entry: ConfigEntry) -> None:
        await coordinator.async_reset_quiz_for_all()

    entry.async_on_unload(entry.add_update_listener(_options_updated))
    refresh = entry.options.get(CONF_REFRESH_TIME, entry.data.get(CONF_REFRESH_TIME, "00:00:00"))
    hour, minute, second = (int(value) for value in refresh.split(":"))
    entry.async_on_unload(
            async_track_time_change(
                hass,
                lambda _now: hass.async_create_task(coordinator.async_refresh()),
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

    async def start(call: ServiceCall) -> None:
        user_id = await require_user(call)
        for coordinator in await get_coordinators(call):
            await coordinator.async_start_quiz(user_id)

    async def answer(call: ServiceCall) -> None:
        user_id = await require_user(call)
        for coordinator in await get_coordinators(call):
            await coordinator.async_answer_question(user_id, int(call.data["question_index"]), call.data["answer"])

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
    hass.services.async_register(DOMAIN, SERVICE_NEW, start)
    hass.services.async_register(DOMAIN, SERVICE_ANSWER, answer)
    hass.services.async_register(DOMAIN, SERVICE_NEXT, next_question)
    hass.services.async_register(DOMAIN, SERVICE_RESET, reset)
    hass.services.async_register(DOMAIN, SERVICE_REFRESH, refresh)
