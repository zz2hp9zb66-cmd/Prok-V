"""Safe-area grid for a vertical frame."""

from __future__ import annotations

from dataclasses import dataclass

from prokv.config import VideoSpec
from prokv.style import Spacing


@dataclass(frozen=True)
class Grid:
    width: int
    height: int
    left: int
    right: int
    top: int
    bottom: int

    @classmethod
    def for_spec(cls, spec: VideoSpec, spacing: Spacing) -> "Grid":
        return cls(spec.width, spec.height, spacing.margin_x, spec.width - spacing.margin_x,
                   spacing.safe_top, spec.height - spacing.safe_bottom)

    @property
    def content_w(self) -> int:
        return self.right - self.left

    @property
    def content_h(self) -> int:
        return self.bottom - self.top

    @property
    def center_x(self) -> float:
        return self.width / 2
