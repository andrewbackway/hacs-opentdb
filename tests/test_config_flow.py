from homeassistant.config_entries import SOURCE_USER
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.opentdb.const import DOMAIN


async def test_user_step_allows_multiple_quizzes(hass):
    MockConfigEntry(domain=DOMAIN, title="Existing Quiz", data={}).add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": SOURCE_USER})

    assert result["type"] == "menu"
    assert result["step_id"] == "user"
