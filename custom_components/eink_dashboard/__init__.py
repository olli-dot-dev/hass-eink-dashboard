from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .http import EinkPublicImageView
from .store import EinkDashboardStore

PLATFORMS = ["image"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    hass.data.setdefault(DOMAIN, {})

    store = EinkDashboardStore(hass, entry.entry_id)
    widgets = await store.async_load()
    hass.data[DOMAIN][entry.entry_id] = {"store": store, "widgets": widgets}

    if not hass.data[DOMAIN].get("_view_registered"):
        hass.http.register_view(EinkPublicImageView())
        hass.data[DOMAIN]["_view_registered"] = True

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return ok
