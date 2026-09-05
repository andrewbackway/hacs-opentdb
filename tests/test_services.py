from unittest.mock import AsyncMock, MagicMock

import pytest
from homeassistant.core import Context

from custom_components.opentdb import __init__ as opentdb_init
from custom_components.opentdb.const import (
    DOMAIN,
    SERVICE_ANSWER,
    SERVICE_NEW,
    SERVICE_NEXT,
    SERVICE_REFRESH,
    SERVICE_REFRESH_QUESTIONS,
    SERVICE_RESET,
    SERVICE_START,
)


async def _register_test_services(hass, monkeypatch, coordinators):
    hass.data[DOMAIN] = coordinators
    target_ids = list(coordinators)
    extract_ids = AsyncMock(return_value=target_ids)
    monkeypatch.setattr(opentdb_init, "async_extract_config_entry_ids", extract_ids)
    await opentdb_init.async_setup(hass, {})
    return extract_ids


@pytest.mark.parametrize(
    ("service", "method", "data", "expected_args", "expected_kwargs"),
    [
        (SERVICE_START, "async_start_quiz", {}, ("user_1",), {}),
        (SERVICE_NEW, "async_start_quiz", {}, ("user_1",), {"force_new": True}),
        (SERVICE_REFRESH_QUESTIONS, "async_start_quiz", {}, ("user_1",), {"force_new": True}),
        (
            SERVICE_ANSWER,
            "async_answer_question",
            {"question_index": 2, "answer": "Answer"},
            ("user_1", 2, "Answer"),
            {},
        ),
        (SERVICE_NEXT, "async_next_question", {}, ("user_1",), {}),
        (SERVICE_RESET, "async_reset_quiz", {}, ("user_1",), {}),
    ],
)
async def test_user_services_await_target_resolution(
    hass, monkeypatch, service, method, data, expected_args, expected_kwargs
):
    coordinator = AsyncMock()
    coordinator.set_player_name = MagicMock()
    extract_ids = await _register_test_services(hass, monkeypatch, {"entry_1": coordinator})

    await hass.services.async_call(
        DOMAIN,
        service,
        {**data, "entity_id": "sensor.trivia_quiz_quiz"},
        blocking=True,
        context=Context(user_id="user_1"),
    )

    extract_ids.assert_awaited_once()
    getattr(coordinator, method).assert_awaited_once_with(*expected_args, **expected_kwargs)


async def test_refresh_awaits_target_resolution_without_user(hass, monkeypatch):
    coordinator = AsyncMock()
    extract_ids = await _register_test_services(hass, monkeypatch, {"entry_1": coordinator})

    await hass.services.async_call(
        DOMAIN,
        SERVICE_REFRESH,
        {"entity_id": "sensor.trivia_quiz_quiz"},
        blocking=True,
    )

    extract_ids.assert_awaited_once()
    coordinator.async_refresh.assert_awaited_once_with()


async def test_targeted_service_only_calls_selected_coordinator(hass, monkeypatch):
    first = AsyncMock()
    second = AsyncMock()
    hass.data[DOMAIN] = {"entry_1": first, "entry_2": second}
    extract_ids = AsyncMock(return_value=["entry_1"])
    monkeypatch.setattr(opentdb_init, "async_extract_config_entry_ids", extract_ids)
    await opentdb_init.async_setup(hass, {})

    await hass.services.async_call(
        DOMAIN,
        SERVICE_NEXT,
        {"entity_id": "sensor.first_quiz_quiz"},
        blocking=True,
        context=Context(user_id="user_1"),
    )

    extract_ids.assert_awaited_once()
    first.async_next_question.assert_awaited_once_with("user_1")
    second.async_next_question.assert_not_awaited()


@pytest.mark.parametrize(
    "service",
    [
        SERVICE_START,
        SERVICE_NEW,
        SERVICE_REFRESH_QUESTIONS,
        SERVICE_ANSWER,
        SERVICE_NEXT,
        SERVICE_RESET,
    ],
)
async def test_user_services_require_authenticated_context(hass, monkeypatch, service):
    coordinator = AsyncMock()
    await _register_test_services(hass, monkeypatch, {"entry_1": coordinator})
    data = {"entity_id": "sensor.trivia_quiz_quiz"}
    if service == SERVICE_ANSWER:
        data.update(question_index=0, answer="Answer")

    with pytest.raises(ValueError, match="authenticated Home Assistant user"):
        await hass.services.async_call(DOMAIN, service, data, blocking=True)
