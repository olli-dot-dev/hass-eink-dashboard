from __future__ import annotations

from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.storage import Store

_STORAGE_VERSION = 1


class EinkDashboardStore:
    def __init__(self, hass: HomeAssistant, entry_id: str) -> None:
        self._store: Store[list[dict[str, Any]]] = Store(
            hass, _STORAGE_VERSION, f"eink_dashboard.{entry_id}"
        )

    async def async_load(self) -> list[dict[str, Any]]:
        data = await self._store.async_load()
        if data is None:
            return []
        return data

    async def async_save(self, widgets: list[dict[str, Any]]) -> None:
        await self._store.async_save(widgets)
