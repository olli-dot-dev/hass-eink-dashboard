from __future__ import annotations

import functools
import io
from collections.abc import Callable
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

from .const import (
    Align,
    COLOR_BLACK,
    COLOR_LIGHT_GRAY,
    COLOR_WHITE,
    PADDING,
    WidgetType,
)

type Widget = dict[str, Any]
type DisplayConfig = dict[str, Any]
type RendererFn = Callable[[ImageDraw.ImageDraw, Widget, DisplayConfig], None]

_FONTS_DIR = Path(__file__).parent / "fonts"


@functools.lru_cache(maxsize=None)
def _load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    ttf_path = _FONTS_DIR / "DejaVuSans.ttf"
    if ttf_path.exists():
        return ImageFont.truetype(str(ttf_path), size)
    return ImageFont.load_default(size)


def render_text(
    draw: ImageDraw.ImageDraw,
    widget: Widget,
    config: DisplayConfig,
) -> None:
    x = widget.get("x", PADDING)
    y = widget.get("y", 0)
    text = widget.get("text", "")
    font_size = widget.get("font_size", 22)
    color = widget.get("color", COLOR_BLACK)
    align = widget.get("align", Align.LEFT)

    font = _load_font(font_size)
    width = config["width"]

    if align in (Align.RIGHT, Align.CENTER):
        bbox = draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        if align == Align.RIGHT:
            x = width - PADDING - text_w
        else:
            x = (width - text_w) // 2

    draw.text((x, y), text, fill=color, font=font)


def render_line(
    draw: ImageDraw.ImageDraw,
    widget: Widget,
    _config: DisplayConfig,
) -> None:
    x = widget.get("x", PADDING)
    y = widget.get("y", 0)
    x2 = widget.get("x2", x)
    y2 = widget.get("y2", y)
    color = widget.get("color", COLOR_LIGHT_GRAY)
    width = widget.get("width", 1)
    draw.line([(x, y), (x2, y2)], fill=color, width=width)


def render_separator(
    draw: ImageDraw.ImageDraw,
    widget: Widget,
    config: DisplayConfig,
) -> None:
    y = widget.get("y", 0)
    color = widget.get("color", COLOR_LIGHT_GRAY)
    x0 = widget.get("x", PADDING)
    x1 = config["width"] - PADDING
    draw.line([(x0, y), (x1, y)], fill=color, width=1)


_RENDERERS: dict[WidgetType, RendererFn] = {
    WidgetType.TEXT: render_text,
    WidgetType.LINE: render_line,
    WidgetType.SEPARATOR: render_separator,
}


def render_dashboard(
    widget_list: list[Widget],
    config: DisplayConfig,
) -> bytes:
    config = {"width": 600, "height": 800, **config}
    w = config["width"]
    h = config["height"]
    img = Image.new("L", (w, h), COLOR_WHITE)
    draw = ImageDraw.Draw(img)

    for widget in widget_list:
        renderer = _RENDERERS.get(widget.get("type"))
        if renderer is not None:
            renderer(draw, widget, config)

    rotation = config.get("rotation", 0)
    if rotation:
        img = img.rotate(rotation, expand=True)

    buf = io.BytesIO()
    img.save(buf, "PNG")
    return buf.getvalue()
