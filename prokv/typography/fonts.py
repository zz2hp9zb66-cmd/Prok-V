"""Font loading by role (display, text, mono, ...) from the style's candidate lists."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from PIL import ImageFont

from prokv.style import Fonts


class FontBook:
    def __init__(self, fonts: Fonts) -> None:
        self.paths = {}
        for role in fonts.__dataclass_fields__:
            candidates = getattr(fonts, role)
            self.paths[role] = next((p for p in candidates if Path(p).is_file()), None)

    def get(self, role: str, size: int) -> ImageFont.FreeTypeFont:
        return _load(self.paths.get(role), max(int(size), 6))

    def missing(self) -> list[str]:
        return [role for role, path in self.paths.items() if path is None]


@lru_cache(maxsize=256)
def _load(path: str | None, size: int) -> ImageFont.FreeTypeFont:
    if path is None:
        return ImageFont.load_default(size)  # Latin only: install the fonts listed in style.Fonts
    return ImageFont.truetype(path, size)
