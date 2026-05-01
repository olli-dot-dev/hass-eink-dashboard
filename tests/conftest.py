from __future__ import annotations

import sys
from types import ModuleType
from unittest.mock import MagicMock


def _stub_module(name: str) -> ModuleType:
    mod = ModuleType(name)
    mod.__dict__.setdefault("__path__", [])
    return mod


_HA_MODULES = [
    "homeassistant",
    "homeassistant.components",
    "homeassistant.components.image",
    "homeassistant.config_entries",
    "homeassistant.core",
    "homeassistant.helpers",
    "homeassistant.helpers.event",
    "homeassistant.util",
    "homeassistant.util.dt",
]

for _mod_name in _HA_MODULES:
    if _mod_name not in sys.modules:
        sys.modules[_mod_name] = _stub_module(_mod_name)

image_mod = sys.modules["homeassistant.components.image"]
image_mod.ImageEntity = type(  # type: ignore[attr-defined]
    "ImageEntity",
    (),
    {
        "__init__": lambda self, hass: setattr(self, "hass", hass),
        "_attr_image_last_updated": None,
        "async_write_ha_state": lambda self: None,
    },
)

config_entries = sys.modules["homeassistant.config_entries"]
config_entries.ConfigEntry = MagicMock  # type: ignore[attr-defined]

core_mod = sys.modules["homeassistant.core"]
core_mod.HomeAssistant = MagicMock  # type: ignore[attr-defined]

event_mod = sys.modules["homeassistant.helpers.event"]
event_mod.async_track_time_interval = MagicMock()  # type: ignore[attr-defined]

dt_mod = sys.modules["homeassistant.util.dt"]
dt_mod.utcnow = MagicMock()  # type: ignore[attr-defined]
