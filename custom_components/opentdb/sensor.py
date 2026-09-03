from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import QuizDataUpdateCoordinator


@dataclass(frozen=True, kw_only=True)
class QuizSensorDescription(SensorEntityDescription):
    value_fn: Callable[[dict[str, Any]], Any]
    attributes_fn: Callable[[dict[str, Any]], dict[str, Any]] = lambda _data: {}


SENSORS: tuple[QuizSensorDescription, ...] = (
    QuizSensorDescription(key="quiz", translation_key="quiz", icon="mdi:gamepad-variant", value_fn=lambda data: data.get("state"), attributes_fn=lambda data: {key: data.get(key) for key in ("quiz_name", "set_id", "question_index", "total_questions", "feedback")}),
    QuizSensorDescription(key="question", translation_key="question", icon="mdi:help-circle-outline", value_fn=lambda data: (data.get("question") or {}).get("question"), attributes_fn=lambda data: data.get("question") or {}),
    QuizSensorDescription(key="score", translation_key="score", icon="mdi:trophy-outline", value_fn=lambda data: (data.get("score") or {}).get("correct", 0), attributes_fn=lambda data: data.get("score") or {}),
    QuizSensorDescription(key="elapsed_time", translation_key="elapsed_time", icon="mdi:timer-outline", native_unit_of_measurement="s", value_fn=lambda data: data.get("elapsed_seconds", 0)),
    QuizSensorDescription(key="player_statistics", translation_key="player_statistics", icon="mdi:account-chart-outline", value_fn=lambda data: (data.get("player_stats") or {}).get("questions", 0), attributes_fn=lambda data: data.get("player_stats") or {}),
    QuizSensorDescription(key="quiz_statistics", translation_key="quiz_statistics", icon="mdi:chart-box-outline", value_fn=lambda data: (data.get("quiz_stats") or {}).get("questions", 0), attributes_fn=lambda data: data.get("quiz_stats") or {}),
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    coordinator: QuizDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(QuizSensor(coordinator, entry, description) for description in SENSORS)


class QuizSensor(CoordinatorEntity[QuizDataUpdateCoordinator], SensorEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator: QuizDataUpdateCoordinator, entry: ConfigEntry, description: QuizSensorDescription) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_device_info = DeviceInfo(identifiers={(DOMAIN, entry.entry_id)}, name=entry.title, manufacturer="Open Trivia Database", model="Quiz")

    @property
    def native_value(self) -> Any:
        return self.entity_description.value_fn(self.coordinator.data or {})

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {key: value for key, value in self.entity_description.attributes_fn(self.coordinator.data or {}).items() if value is not None}
