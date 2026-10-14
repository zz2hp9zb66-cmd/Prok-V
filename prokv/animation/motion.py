"""Entrance motions. Each Motion describes how an element arrives at its resting state.

Combine: fade, slide (dx/dy in px, or dy_rel in multiples of the element height),
scale, progressive reveal ("right"/"left"/"down"/"up"/"radial": lines drawing,
blocks wiping in) and mask (clip to own box, so text rises from behind a line).
"""

from __future__ import annotations

from dataclasses import dataclass, replace


@dataclass(frozen=True)
class Motion:
    fade: bool = True
    dx: float = 0.0
    dy: float = 0.0
    dy_rel: float = 0.0
    scale_from: float = 1.0
    reveal: str | None = None
    mask: bool = False
    easing: str | None = None   # None = style default

    def with_(self, **kwargs) -> "Motion":
        return replace(self, **kwargs)


PRESETS = {
    "fade": Motion(),
    "fade_up": Motion(dy=36),
    "fade_left": Motion(dx=40),      # arrives from the right
    "fade_right": Motion(dx=-40),    # arrives from the left
    "mask_up": Motion(fade=True, dy_rel=0.9, mask=True),
    "scale_in": Motion(scale_from=0.94),
    "draw_right": Motion(fade=False, reveal="right"),
    "draw_left": Motion(fade=False, reveal="left"),
    "draw_down": Motion(fade=False, reveal="down"),
    "draw_up": Motion(fade=False, reveal="up"),
    "draw_radial": Motion(fade=False, reveal="radial"),
    "wipe_right": Motion(fade=False, reveal="right", easing="ease_in_out"),
    "none": Motion(fade=False),
}
