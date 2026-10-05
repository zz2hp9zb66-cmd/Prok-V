"""Sprite factories: each returns an RGBA image of one graphic element.

Curves and diagonals are drawn at SS× resolution and downsampled for clean
anti-aliased edges.
"""

from __future__ import annotations

from PIL import Image, ImageDraw

SS = 3  # supersampling factor


def _canvas(w: int, h: int, scale: int = 1) -> tuple[Image.Image, ImageDraw.ImageDraw]:
    image = Image.new("RGBA", (max(int(w * scale), 1), max(int(h * scale), 1)), (0, 0, 0, 0))
    return image, ImageDraw.Draw(image)


def _down(image: Image.Image, w: int, h: int) -> Image.Image:
    return image.resize((max(int(w), 1), max(int(h), 1)), Image.Resampling.LANCZOS)


def rule(length: int, thickness: int, color: str, vertical: bool = False) -> Image.Image:
    size = (thickness, length) if vertical else (length, thickness)
    return Image.new("RGBA", (max(size[0], 1), max(size[1], 1)), color)


def block(w: int, h: int, color: str) -> Image.Image:
    return Image.new("RGBA", (max(w, 1), max(h, 1)), color)


def frame(w: int, h: int, color: str, width: int = 2) -> Image.Image:
    image, draw = _canvas(w, h)
    draw.rectangle((0, 0, w - 1, h - 1), outline=color, width=width)
    return image


def circle(d: int, color: str, outline: int = 0) -> Image.Image:
    image, draw = _canvas(d, d, SS)
    box = (0, 0, d * SS - 1, d * SS - 1)
    if outline:
        draw.ellipse(box, outline=color, width=outline * SS)
    else:
        draw.ellipse(box, fill=color)
    return _down(image, d, d)


def ring(d: int, width: int, color: str, extent: float = 360.0) -> Image.Image:
    """Arc starting at 12 o'clock, clockwise, covering `extent` degrees."""
    image, draw = _canvas(d, d, SS)
    draw.arc((0, 0, d * SS - 1, d * SS - 1), -90, -90 + extent, fill=color, width=width * SS)
    return _down(image, d, d)


def arrow(length: int, color: str, thickness: int = 3, head: int = 18, direction: str = "down") -> Image.Image:
    """Thin arrow with an open chevron head. direction: "down" or "right"."""
    if direction == "right":
        return arrow(length, color, thickness, head, "down").rotate(90, expand=True)
    w = head * 2 + thickness
    image, draw = _canvas(w, length, SS)
    cx = w * SS / 2
    t = thickness * SS
    draw.line((cx, 0, cx, length * SS - t), fill=color, width=t)
    tip = length * SS - t / 2
    draw.line((cx - head * SS, tip - head * SS, cx, tip), fill=color, width=t, joint="curve")
    draw.line((cx + head * SS, tip - head * SS, cx, tip), fill=color, width=t, joint="curve")
    return _down(image, w, length)


def dot(d: int, color: str) -> Image.Image:
    return circle(d, color)


def vinyl(d: int, disc: str, groove: str, label: str, hole: str) -> Image.Image:
    """A vinyl record: disc, fine grooves, centre label and spindle hole."""
    image, draw = _canvas(d, d, SS)
    D = d * SS
    draw.ellipse((0, 0, D - 1, D - 1), fill=disc)
    r = D / 2
    for k in range(int(r * 0.40), int(r * 0.97), 7 * SS):
        draw.ellipse((r - k, r - k, r + k, r + k), outline=groove, width=SS)
    lr = r * 0.33
    draw.ellipse((r - lr, r - lr, r + lr, r + lr), fill=label)
    draw.ellipse((r - lr * 0.86, r - lr * 0.86, r + lr * 0.86, r + lr * 0.86), outline=disc, width=SS)
    hr = r * 0.035
    draw.ellipse((r - hr, r - hr, r + hr, r + hr), fill=hole)
    return _down(image, d, d)


def quote_mark(font, color: str, glyph: str = "«") -> Image.Image:
    ascent, descent = font.getmetrics()
    w = int(font.getlength(glyph)) + 8
    image, draw = _canvas(w, ascent + descent)
    draw.text((4, ascent), glyph, font=font, anchor="ls", fill=color)
    return image
