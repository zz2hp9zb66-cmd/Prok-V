"""Backgrounds: flat palette colour with a subtle paper grain."""

from __future__ import annotations

from functools import lru_cache

from PIL import Image, ImageChops


def add_grain(image: Image.Image, amount: int) -> Image.Image:
    """Monochrome Gaussian grain (std-dev `amount`) on an RGB image."""
    if amount <= 0:
        return image
    noise = Image.effect_noise(image.size, amount)
    return ImageChops.add(image, Image.merge("RGB", (noise, noise, noise)), 1.0, -128)


@lru_cache(maxsize=16)
def paper(size: tuple[int, int], color: str, grain: int) -> Image.Image:
    return add_grain(Image.new("RGB", size, color), grain)
