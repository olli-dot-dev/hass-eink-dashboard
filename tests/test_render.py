from __future__ import annotations

import io

from PIL import Image

from custom_components.eink_dashboard.const import PADDING
from custom_components.eink_dashboard.render import (
    render_dashboard,
)


def _png_to_image(png_bytes: bytes) -> Image.Image:
    return Image.open(io.BytesIO(png_bytes))


def _pixel(img: Image.Image, x: int, y: int) -> int:
    val = img.getpixel((x, y))
    assert isinstance(val, int)
    return val


class TestRenderDashboard:
    def test_empty_widget_list_returns_white_image(self) -> None:
        config = {"width": 100, "height": 100}
        result = render_dashboard([], config)

        img = _png_to_image(result)
        assert img.mode == "L"
        assert img.size == (100, 100)
        assert _pixel(img, 50, 50) == 255

    def test_returns_valid_png(self) -> None:
        config = {"width": 200, "height": 300}
        result = render_dashboard([], config)

        img = _png_to_image(result)
        assert img.format == "PNG"
        assert img.size == (200, 300)

    def test_rotation_90(self) -> None:
        config = {"width": 200, "height": 100, "rotation": 90}
        result = render_dashboard([], config)

        img = _png_to_image(result)
        assert img.size == (100, 200)

    def test_rotation_270(self) -> None:
        config = {"width": 200, "height": 100, "rotation": 270}
        result = render_dashboard([], config)

        img = _png_to_image(result)
        assert img.size == (100, 200)

    def test_unknown_widget_type_is_skipped(self) -> None:
        config = {"width": 100, "height": 100}
        widgets = [{"type": "nonexistent", "x": 10, "y": 10}]
        result = render_dashboard(widgets, config)

        img = _png_to_image(result)
        assert img.size == (100, 100)


class TestRenderText:
    def test_text_draws_pixels(self) -> None:
        config = {"width": 200, "height": 100}
        widgets = [
            {
                "type": "text",
                "x": 10,
                "y": 10,
                "text": "Hello",
                "font_size": 20,
            }
        ]
        result = render_dashboard(widgets, config)

        img = _png_to_image(result)
        has_dark_pixel = any(
            _pixel(img, x, y) < 128
            for x in range(10, 100)
            for y in range(10, 40)
        )
        assert has_dark_pixel

    def test_text_right_align(self) -> None:
        config = {"width": 200, "height": 100}
        widgets = [
            {
                "type": "text",
                "x": 0,
                "y": 10,
                "text": "Hi",
                "font_size": 20,
                "align": "right",
            }
        ]
        result = render_dashboard(widgets, config)

        img = _png_to_image(result)
        has_dark_right = any(
            _pixel(img, x, y) < 128
            for x in range(140, 200)
            for y in range(10, 40)
        )
        assert has_dark_right

    def test_text_center_align(self) -> None:
        config = {"width": 200, "height": 100}
        widgets = [
            {
                "type": "text",
                "x": 0,
                "y": 10,
                "text": "Hi",
                "font_size": 20,
                "align": "center",
            }
        ]
        result = render_dashboard(widgets, config)

        img = _png_to_image(result)
        has_dark_center = any(
            _pixel(img, x, y) < 128
            for x in range(80, 120)
            for y in range(10, 40)
        )
        assert has_dark_center

    def test_text_custom_color(self) -> None:
        config = {"width": 200, "height": 100}
        widgets = [
            {
                "type": "text",
                "x": 10,
                "y": 10,
                "text": "Gray",
                "font_size": 20,
                "color": 160,
            }
        ]
        result = render_dashboard(widgets, config)

        img = _png_to_image(result)
        has_gray_pixel = any(
            100 < _pixel(img, x, y) < 200
            for x in range(10, 80)
            for y in range(10, 40)
        )
        assert has_gray_pixel


class TestRenderLine:
    def test_horizontal_line(self) -> None:
        config = {"width": 100, "height": 100}
        widgets = [
            {
                "type": "line",
                "x": 10,
                "y": 50,
                "x2": 90,
                "y2": 50,
                "color": 0,
            }
        ]
        result = render_dashboard(widgets, config)

        img = _png_to_image(result)
        assert _pixel(img, 50, 50) == 0
        assert _pixel(img, 50, 10) == 255

    def test_line_custom_color(self) -> None:
        config = {"width": 100, "height": 100}
        widgets = [
            {
                "type": "line",
                "x": 0,
                "y": 50,
                "x2": 99,
                "y2": 50,
                "color": 160,
            }
        ]
        result = render_dashboard(widgets, config)

        img = _png_to_image(result)
        assert _pixel(img, 50, 50) == 160


class TestRenderSeparator:
    def test_separator_spans_width(self) -> None:
        config = {"width": 200, "height": 100}
        widgets = [{"type": "separator", "y": 50, "color": 0}]
        result = render_dashboard(widgets, config)

        img = _png_to_image(result)
        assert _pixel(img, PADDING, 50) == 0
        assert _pixel(img, 175, 50) == 0
        # Outside separator range should be white
        assert _pixel(img, 10, 50) == 255

    def test_separator_default_color(self) -> None:
        config = {"width": 200, "height": 100}
        widgets = [{"type": "separator", "y": 50}]
        result = render_dashboard(widgets, config)

        img = _png_to_image(result)
        # Default is COLOR_LIGHT_GRAY = 210
        assert _pixel(img, 100, 50) == 210
