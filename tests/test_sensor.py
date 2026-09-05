from datetime import datetime, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock

from homeassistant.components.sensor import SensorDeviceClass

from custom_components.opentdb.sensor import SENSORS, QuizSensor


def test_same_quiz_names_keep_unique_sensor_ids():
    coordinator = MagicMock()
    first_entry = SimpleNamespace(entry_id="entry_1", title="Same Quiz", data={})
    second_entry = SimpleNamespace(entry_id="entry_2", title="Same Quiz", data={})

    first_ids = {
        QuizSensor(coordinator, first_entry, description)._attr_unique_id for description in SENSORS
    }
    second_ids = {
        QuizSensor(coordinator, second_entry, description)._attr_unique_id
        for description in SENSORS
    }

    assert first_ids.isdisjoint(second_ids)
    assert {unique_id.removeprefix("entry_1_") for unique_id in first_ids} == {
        description.key for description in SENSORS
    }
    assert {unique_id.removeprefix("entry_2_") for unique_id in second_ids} == {
        description.key for description in SENSORS
    }


def test_last_questions_reset_sensor_is_timestamp():
    reset_at = "2026-09-05T12:34:56+00:00"
    coordinator = MagicMock()
    coordinator.data = {"last_questions_reset": reset_at}
    entry = SimpleNamespace(entry_id="entry_1", title="Quiz", data={})
    description = next(
        description for description in SENSORS if description.key == "last_questions_reset"
    )

    sensor = QuizSensor(coordinator, entry, description)

    assert sensor.device_class is SensorDeviceClass.TIMESTAMP
    assert sensor.native_value == datetime(2026, 9, 5, 12, 34, 56, tzinfo=timezone.utc)
