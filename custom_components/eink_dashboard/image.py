from __future__ import annotations

import asyncio
import hashlib
from collections.abc import Callable
from datetime import timedelta
from typing import Any

from homeassistant.components.image import ImageEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import (
    async_track_time_interval,
)
from homeassistant.util import dt as dt_util

from .const import (
    DEFAULT_HEIGHT,
    DEFAULT_UPDATE_INTERVAL,
    DEFAULT_WIDTH,
)
from .render import render_dashboard


class EinkDashboardImage(ImageEntity):
    _attr_content_type = "image/png"

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ConfigEntry,
    ) -> None:
        super().__init__(hass)
        self._entry = entry
        self._widgets: list[dict[str, Any]] = []
        self._rendered: bytes | None = None
        self._etag: str | None = None
        self._unsub: Callable[[], None] | None = None
        self._refresh_lock = asyncio.Lock()
        self._attr_name = entry.title
        self._attr_unique_id = entry.entry_id

    async def async_added_to_hass(self) -> None:
        interval = self._entry.options.get(
            "update_interval", DEFAULT_UPDATE_INTERVAL
        )
        self._unsub = async_track_time_interval(
            self.hass,
            self._async_refresh,
            timedelta(seconds=interval),
        )
        await self._async_refresh(None)

    async def async_will_remove_from_hass(self) -> None:
        if self._unsub:
            self._unsub()

    def set_widgets(self, widgets: list[dict[str, Any]]) -> None:
        self._widgets = widgets

    async def _async_refresh(self, _now: Any) -> None:
        async with self._refresh_lock:
            config = {
                "width": self._entry.options.get("width", DEFAULT_WIDTH),
                "height": self._entry.options.get("height", DEFAULT_HEIGHT),
                "rotation": self._entry.options.get("rotation", 0),
                "states": self._build_states(),
            }
            new_bytes = await self.hass.async_add_executor_job(
                render_dashboard, self._widgets, config
            )
            if new_bytes != self._rendered:
                self._rendered = new_bytes
                self._etag = f'"{hashlib.sha256(new_bytes).hexdigest()}"'
                self._attr_image_last_updated = dt_util.utcnow()
                self.async_write_ha_state()

    def _build_states(self) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for state in self.hass.states.async_all():
            result[state.entity_id] = {
                "state": state.state,
                "attributes": dict(state.attributes),
            }
        return result

    @property
    def etag(self) -> str | None:
        return self._etag

    async def async_image(self) -> bytes | None:
        return self._rendered
