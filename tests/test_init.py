from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

from custom_components.eink_dashboard import (
    async_setup_entry,
    async_unload_entry,
)
from custom_components.eink_dashboard.const import DOMAIN
from custom_components.eink_dashboard.http import EinkPublicImageView


def _make_entry(entry_id: str = "entry1") -> MagicMock:
    entry = MagicMock()
    entry.entry_id = entry_id
    return entry


def _make_hass() -> MagicMock:
    hass = MagicMock()
    hass.data = {}
    hass.config_entries.async_forward_entry_setups = AsyncMock()
    hass.config_entries.async_unload_platforms = AsyncMock(return_value=True)
    return hass


class TestAsyncSetupEntry:
    async def test_populates_hass_data(self) -> None:
        hass = _make_hass()
        entry = _make_entry()
        widgets = [{"type": "separator", "y": 10}]

        with patch(
            "custom_components.eink_dashboard.EinkDashboardStore"
        ) as MockStore:
            MockStore.return_value.async_load = AsyncMock(return_value=widgets)
            await async_setup_entry(hass, entry)

        assert entry.entry_id in hass.data[DOMAIN]
        data = hass.data[DOMAIN][entry.entry_id]
        assert "store" in data
        assert data["widgets"] == widgets

    async def test_registers_http_view(self) -> None:
        hass = _make_hass()
        entry = _make_entry()

        with patch(
            "custom_components.eink_dashboard.EinkDashboardStore"
        ) as MockStore:
            MockStore.return_value.async_load = AsyncMock(return_value=[])
            await async_setup_entry(hass, entry)

        hass.http.register_view.assert_called_once()
        view = hass.http.register_view.call_args[0][0]
        assert isinstance(view, EinkPublicImageView)

    async def test_registers_http_view_once_for_multiple_entries(
        self,
    ) -> None:
        hass = _make_hass()

        with patch(
            "custom_components.eink_dashboard.EinkDashboardStore"
        ) as MockStore:
            MockStore.return_value.async_load = AsyncMock(return_value=[])
            await async_setup_entry(hass, _make_entry("e1"))
            await async_setup_entry(hass, _make_entry("e2"))

        hass.http.register_view.assert_called_once()

    async def test_forwards_to_image_platform(self) -> None:
        hass = _make_hass()
        entry = _make_entry()

        with patch(
            "custom_components.eink_dashboard.EinkDashboardStore"
        ) as MockStore:
            MockStore.return_value.async_load = AsyncMock(return_value=[])
            await async_setup_entry(hass, entry)

        hass.config_entries.async_forward_entry_setups.assert_called_once_with(
            entry, ["image"]
        )

    async def test_returns_true(self) -> None:
        hass = _make_hass()
        entry = _make_entry()

        with patch(
            "custom_components.eink_dashboard.EinkDashboardStore"
        ) as MockStore:
            MockStore.return_value.async_load = AsyncMock(return_value=[])
            result = await async_setup_entry(hass, entry)

        assert result is True


class TestAsyncUnloadEntry:
    async def test_unloads_platforms(self) -> None:
        hass = _make_hass()
        entry = _make_entry()
        hass.data = {DOMAIN: {entry.entry_id: {"store": MagicMock()}}}

        result = await async_unload_entry(hass, entry)

        hass.config_entries.async_unload_platforms.assert_called_once_with(
            entry, ["image"]
        )
        assert result is True

    async def test_removes_entry_data_on_success(self) -> None:
        hass = _make_hass()
        entry = _make_entry()
        hass.data = {DOMAIN: {entry.entry_id: {"store": MagicMock()}}}

        await async_unload_entry(hass, entry)

        assert entry.entry_id not in hass.data[DOMAIN]

    async def test_keeps_entry_data_on_failure(self) -> None:
        hass = _make_hass()
        hass.config_entries.async_unload_platforms = AsyncMock(
            return_value=False
        )
        entry = _make_entry()
        hass.data = {DOMAIN: {entry.entry_id: {"store": MagicMock()}}}

        result = await async_unload_entry(hass, entry)

        assert result is False
        assert entry.entry_id in hass.data[DOMAIN]
