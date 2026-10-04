"""Animated elements: a pre-rendered sprite + resting position + timing + motion.

Sprites are drawn once; every frame only transforms them (offset, crop, mask,
scale, opacity), which keeps rendering fast.
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass
from typing import Callable

from PIL import Image, ImageChops, ImageDraw

from prokv.animation.easing import ease
from prokv.animation.motion import Motion


@dataclass
class Element:
    sprite: Image.Image
    x: float
    y: float
    start: float
    duration: float
    motion: Motion
    exits: bool = True          # fades out at the end of the scene
    default_easing: str = "ease_out_quart"

    def progress(self, t: float) -> float:
        if t < self.start:
            return 0.0
        if self.duration <= 0:
            return 1.0
        return ease(self.motion.easing or self.default_easing, (t - self.start) / self.duration)

    def sprite_at(self, p: float) -> Image.Image:
        return self.sprite

    def anchor_shift(self, sprite: Image.Image) -> float:
        return 0.0

    def draw(self, frame: Image.Image, t: float, offset: tuple[float, float] = (0, 0),
             exit_p: float = 0.0, exit_dy: float = 0.0) -> None:
        if t < self.start:
            return
        m = self.motion
        p = self.progress(t)
        img = self.sprite_at(p)
        w, h = img.size
        x = self.x + offset[0] + self.anchor_shift(img)
        y = self.y + offset[1]
        if self.exits and exit_p > 0:
            y -= exit_dy * exit_p

        if m.reveal and p < 1:
            if p <= 0:
                return
            if m.reveal == "right":
                img = img.crop((0, 0, max(1, math.ceil(w * p)), h))
            elif m.reveal == "left":
                cut = int(w * (1 - p))
                img = img.crop((cut, 0, w, h))
                x += cut
            elif m.reveal == "down":
                img = img.crop((0, 0, w, max(1, math.ceil(h * p))))
            elif m.reveal == "up":
                cut = int(h * (1 - p))
                img = img.crop((0, cut, w, h))
                y += cut
            elif m.reveal == "radial":
                mask = Image.new("L", (w, h), 0)
                ImageDraw.Draw(mask).pieslice((-w, -h, 2 * w, 2 * h), -90, -90 + 360 * p, fill=255)
                img = img.copy()
                img.putalpha(ImageChops.multiply(img.getchannel("A"), mask))

        remaining = 1 - p
        dy = m.dy * remaining + m.dy_rel * h * remaining
        if m.mask:
            shift = int(round(dy))
            if shift >= img.height:
                return
            if shift > 0:
                img = img.crop((0, 0, img.width, img.height - shift))
                y += shift
        else:
            x += m.dx * remaining
            y += dy

        if m.scale_from != 1.0 and p < 1:
            s = m.scale_from + (1 - m.scale_from) * p
            nw, nh = max(1, round(img.width * s)), max(1, round(img.height * s))
            x += (img.width - nw) / 2
            y += (img.height - nh) / 2
            img = img.resize((nw, nh), Image.Resampling.BILINEAR)

        opacity = (p if m.fade else 1.0) * (1 - exit_p if self.exits else 1.0)
        if opacity <= 0.003:
            return
        alpha = img.getchannel("A")
        if opacity < 0.997:
            alpha = alpha.point(lambda v: int(v * opacity))
        frame.paste(img, (round(x), round(y)), alpha)


_NUM = re.compile(r"\d+(?:[.,]\d+)?")


def count_text(display: str, p: float) -> str:
    """`display` with its first number scaled by p, keeping decimals and separators."""
    m = _NUM.search(display.replace(" ", ""))
    if not m:
        return display
    raw = m.group(0)
    sep = "," if "," in raw else "."
    decimals = len(raw.split(sep)[1]) if sep in raw else 0
    value = float(raw.replace(",", ".")) * p
    shown = f"{value:.{decimals}f}".replace(".", sep)
    clean = display.replace(" ", "")
    return clean[:m.start()] + shown + clean[m.end():]


@dataclass
class CounterElement(Element):
    """A number that counts up as it enters. `render` draws a given string."""

    render: Callable[[str], Image.Image] | None = None
    text: str = ""
    align: str = "left"   # keeps this edge (or the centre) fixed while digits change

    def __post_init__(self) -> None:
        self._cache: dict[str, Image.Image] = {}

    def sprite_at(self, p: float) -> Image.Image:
        if p >= 1 or self.render is None:
            return self.sprite
        value = count_text(self.text, p)
        if value not in self._cache:
            self._cache[value] = self.render(value)
        return self._cache[value]

    def anchor_shift(self, sprite: Image.Image) -> float:
        if self.align == "center":
            return (self.sprite.width - sprite.width) / 2
        if self.align == "right":
            return self.sprite.width - sprite.width
        return 0.0
