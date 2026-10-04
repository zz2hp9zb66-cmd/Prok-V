"""Small Pillow helpers shared by generation and rendering."""

from __future__ import annotations

from PIL import Image, ImageChops


def add_grain(image: Image.Image, amount: int) -> Image.Image:
    """Add subtle monochrome film/paper grain (Gaussian, std-dev `amount`) to an RGB image."""
    if amount <= 0:
        return image
    noise = Image.effect_noise(image.size, amount)
    return ImageChops.add(image, Image.merge("RGB", (noise, noise, noise)), 1.0, -128)
