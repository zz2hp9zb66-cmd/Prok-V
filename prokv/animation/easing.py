"""Easing curves. Calm, decelerating curves by default — no bounce, no overshoot."""

from __future__ import annotations

import math

EASINGS = {
    "linear": lambda p: p,
    "ease_in": lambda p: p ** 3,
    "ease_out": lambda p: 1 - (1 - p) ** 3,
    "ease_out_quart": lambda p: 1 - (1 - p) ** 4,
    "ease_out_expo": lambda p: 1.0 if p >= 1 else 1 - 2 ** (-10 * p),
    "ease_in_out": lambda p: 4 * p ** 3 if p < 0.5 else 1 - (-2 * p + 2) ** 3 / 2,
    "ease_in_out_sine": lambda p: 0.5 - 0.5 * math.cos(math.pi * p),
}


def ease(name: str, p: float) -> float:
    p = min(max(p, 0.0), 1.0)
    return EASINGS.get(name, EASINGS["ease_out"])(p)
