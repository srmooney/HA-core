"""Helper to test significant Cover state changes."""
from __future__ import annotations

from typing import Any

from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.significant_change import (
    check_absolute_change,
    check_valid_float,
)

from . import ATTR_CURRENT_POSITION, ATTR_CURRENT_TILT_POSITION

SIGNIFICANT_ATTRIBUTES: set[str] = {
    ATTR_CURRENT_POSITION,
    ATTR_CURRENT_TILT_POSITION,
}


@callback
def async_check_significant_change(
    hass: HomeAssistant,
    old_state: str,
    old_attrs: dict,
    new_state: str,
    new_attrs: dict,
    **kwargs: Any,
) -> bool | None:
    """Test if state significantly changed."""
    if old_state != new_state:
        return True

    old_attrs_s = set(old_attrs.items())
    new_attrs_s = set(new_attrs.items())
    changed_attrs: set[str] = {item[0] for item in old_attrs_s ^ new_attrs_s}

    for attr_name in changed_attrs:
        if attr_name not in SIGNIFICANT_ATTRIBUTES:
            continue

        old_attr_value = old_attrs.get(attr_name)
        new_attr_value = new_attrs.get(attr_name)
        if new_attr_value is None or not check_valid_float(new_attr_value):
            # New attribute value is invalid, ignore it
            continue

        if old_attr_value is None or not check_valid_float(old_attr_value):
            # Old attribute value was invalid, we should report again
            return True

        if check_absolute_change(old_attr_value, new_attr_value, 1.0):
            return True

    # no significant attribute change detected
    return False
