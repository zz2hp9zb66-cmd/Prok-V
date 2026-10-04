"""Stage 1: generate images from a text prompt."""

from __future__ import annotations

import hashlib
from abc import ABC, abstractmethod
from pathlib import Path

from PIL import Image, ImageDraw

from prokv.imaging import add_grain
from prokv.models import GeneratedImage
from prokv.style import DEFAULT_STYLE, VisualStyle


class ImageGenerator(ABC):
    """Turns a prompt into image files on disk."""

    @abstractmethod
    def generate(self, prompt: str, count: int, out_dir: Path) -> list[GeneratedImage]:
        ...


class PlaceholderGenerator(ImageGenerator):
    """Offline stand-in: abstract editorial cards in the visual style's palette.

    Each image is a two-tone palette gradient with one motif (vinyl record, arch
    or band) and fine grain, chosen deterministically from the prompt. Needs no
    network or API keys. Replace with a real generator once one has been chosen.
    """

    def __init__(self, width: int = 768, height: int = 1024, style: VisualStyle = DEFAULT_STYLE) -> None:
        self.width = width
        self.height = height
        self.style = style.placeholder

    def generate(self, prompt: str, count: int, out_dir: Path) -> list[GeneratedImage]:
        out_dir.mkdir(parents=True, exist_ok=True)
        images = []
        for i in range(count):
            digest = hashlib.sha256(f"{prompt}:{i}".encode()).digest()
            path = out_dir / f"image_{i:02d}.png"
            self._draw(digest).save(path)
            images.append(GeneratedImage(path, prompt, self.width, self.height))
        return images

    def _draw(self, digest: bytes) -> Image.Image:
        w, h = self.width, self.height
        schemes = self.style.schemes
        top, bottom, accent = schemes[digest[0] % len(schemes)]
        gradient = Image.linear_gradient("L").resize((w, h))
        image = Image.composite(Image.new("RGB", (w, h), bottom), Image.new("RGB", (w, h), top), gradient)

        draw = ImageDraw.Draw(image)
        shape = digest[1] % 3
        if shape == 0:  # arch
            aw = int(w * 0.56)
            x0, y0 = (w - aw) // 2, int(h * 0.30)
            draw.pieslice((x0, y0, x0 + aw, y0 + aw), 180, 360, fill=accent)
            draw.rectangle((x0, y0 + aw // 2, x0 + aw, int(h * 0.86)), fill=accent)
        elif shape == 1:  # vinyl record
            r = int(w * (0.34 + digest[2] / 255 * 0.08))
            cx, cy = w // 2, int(h * (0.42 + digest[3] / 255 * 0.16))
            draw.ellipse((cx - r, cy - r, cx + r, cy + r), fill=self.style.record_color)
            groove = Image.new("RGB", (1, 1), self.style.record_color).point(lambda v: min(v + 14, 255))
            for gr in range(int(r * 0.42), r - 6, 9):
                draw.ellipse((cx - gr, cy - gr, cx + gr, cy + gr), outline=groove.getpixel((0, 0)))
            lr = int(r * 0.33)
            draw.ellipse((cx - lr, cy - lr, cx + lr, cy + lr), fill=accent)
            draw.ellipse((cx - 6, cy - 6, cx + 6, cy + 6), fill=self.style.record_color)
        else:  # horizontal band with a thin rule
            y = int(h * (0.52 + digest[2] / 255 * 0.14))
            draw.rectangle((0, y, w, y + int(h * 0.16)), fill=accent)
            draw.rectangle((int(w * 0.1), y - int(h * 0.06), int(w * 0.9), y - int(h * 0.06) + 4), fill=accent)
        return add_grain(image, self.style.grain)
