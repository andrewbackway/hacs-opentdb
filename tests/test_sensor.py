from types import SimpleNamespace
from unittest.mock import MagicMock

from custom_components.opentdb.sensor import SENSORS, QuizSensor


def test_same_quiz_names_keep_unique_sensor_ids():
    coordinator = MagicMock()
    first_entry = SimpleNamespace(entry_id="entry_1", title="Same Quiz", data={})
    second_entry = SimpleNamespace(entry_id="entry_2", title="Same Quiz", data={})

    first_ids = {
        QuizSensor(coordinator, first_entry, description)._attr_unique_id
        for description in SENSORS
    }
    second_ids = {
        QuizSensor(coordinator, second_entry, description)._attr_unique_id
        for description in SENSORS
    }

    assert first_ids.isdisjoint(second_ids)
    assert {unique_id.rsplit("_", 1)[-1] for unique_id in first_ids} == {
        description.key for description in SENSORS
    }
    assert {unique_id.rsplit("_", 1)[-1] for unique_id in second_ids} == {
        description.key for description in SENSORS
    }