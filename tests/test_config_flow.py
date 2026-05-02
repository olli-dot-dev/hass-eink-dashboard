from __future__ import annotations

from custom_components.eink_dashboard.config_flow import (
    EinkDashboardConfigFlow,
)


class TestEinkDashboardConfigFlow:
    async def test_step_user_shows_form(self) -> None:
        flow = EinkDashboardConfigFlow()
        result = await flow.async_step_user(None)

        assert result["type"] == "form"
        assert result["step_id"] == "user"
        assert result["data_schema"] is not None

    async def test_step_user_creates_entry(self) -> None:
        flow = EinkDashboardConfigFlow()
        result = await flow.async_step_user(
            {
                "name": "Kitchen",
                "width": 600,
                "height": 800,
                "update_interval": 120,
            }
        )

        assert result["type"] == "create_entry"
        assert result["title"] == "Kitchen"
        assert result["data"] == {}
        assert result["options"] == {
            "width": 600,
            "height": 800,
            "update_interval": 120,
        }
