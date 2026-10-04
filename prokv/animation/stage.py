"""Keyframed stage: persistent nodes, links between them and a camera.

Used for "map" videos where one central object stays on screen and the
composition grows, shrinks and moves around it (instead of separate scenes).

Every Node / Camera holds keyframes. Animations are added in chronological
order with `animate(t, dur, **props)`, `set(t, **props)`, `show(...)`, `hide(...)`.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from PIL import Image

from prokv.animation.easing import ease

_EPS = 1e-4


@dataclass
class _Key:
    t: float
    values: dict
    easing: str = "linear"


class Animated:
    def __init__(self, **initial) -> None:
        self.keys: list[_Key] = [_Key(-1e9, dict(initial))]

    def value(self, t: float) -> dict:
        keys = self.keys
        if t <= keys[0].t:
            return keys[0].values
        for i in range(len(keys) - 1, -1, -1):
            if keys[i].t <= t:
                break
        if i == len(keys) - 1:
            return keys[i].values
        a, b = keys[i], keys[i + 1]
        p = ease(b.easing, (t - a.t) / (b.t - a.t))
        return {k: a.values[k] + (b.values[k] - a.values[k]) * p for k in a.values}

    def animate(self, t: float, dur: float, easing: str = "ease_out_quart", **props) -> "Animated":
        last = self.keys[-1]
        if t < last.t - _EPS:
            raise ValueError(f"Keyframes must be added in time order ({t:.2f} < {last.t:.2f})")
        start = dict(self.value(t))
        if t > last.t + _EPS:
            self.keys.append(_Key(t, start, "linear"))
        t = max(t, last.t)
        self.keys.append(_Key(t + max(dur, _EPS), {**start, **props}, easing))
        return self

    def set(self, t: float, **props) -> "Animated":
        """Jump to new values at time t (no transition)."""
        last = self.keys[-1]
        if t < last.t - _EPS:
            raise ValueError(f"Keyframes must be added in time order ({t:.2f} < {last.t:.2f})")
        current = dict(self.value(t))
        t = max(t, last.t + 2 * _EPS)
        self.keys.append(_Key(t - _EPS, current, "linear"))
        self.keys.append(_Key(t, {**current, **props}, "linear"))
        return self


class Camera(Animated):
    """World point (cx, cy) is shown at the stage's focus point, scaled by zoom."""

    def __init__(self, cx: float, cy: float, zoom: float = 1.0) -> None:
        super().__init__(cx=cx, cy=cy, zoom=zoom)


class Node(Animated):
    """A sprite placed by its centre. Props: x, y, scale, opacity, rot, rise.

    `rise` < 1 clips the sprite to its own box and lowers it inside (mask reveal).
    `fixed` nodes ignore the camera (screen space).
    """

    def __init__(self, sprite: Image.Image, x: float, y: float, z: int = 0, fixed: bool = False,
                 opacity: float = 0.0, scale: float = 1.0) -> None:
        super().__init__(x=x, y=y, scale=scale, opacity=opacity, rot=0.0, rise=1.0)
        self.sprite = sprite
        self.z = z
        self.fixed = fixed
        self.spin: tuple[float, float, float] | None = None          # (start, deg/s, ramp seconds)
        self.pulse: tuple[float, float, float, float] | None = None  # (start, end, beat seconds, amount)
        self._cache: dict = {}

    def show(self, t: float, dur: float = 0.6, dy: float = 30, scale_from: float | None = None,
             rise: bool = False, easing: str = "ease_out_quart") -> "Node":
        v = self.value(t)
        start = {"opacity": 0.0}
        if rise:
            start["rise"] = 0.0
        elif dy:
            start["y"] = v["y"] + dy
        if scale_from is not None:
            start["scale"] = v["scale"] * scale_from
        target = {k: v[k] for k in start}
        target["opacity"] = 1.0
        self.set(t, **start)
        return self.animate(t, dur, easing, **target)

    def hide(self, t: float, dur: float = 0.45, dy: float = -18, easing: str = "ease_in_out") -> "Node":
        v = self.value(t)
        return self.animate(t, dur, easing, opacity=0.0, y=v["y"] + dy)

    def angle(self, t: float, base: float) -> float:
        if not self.spin or t < self.spin[0]:
            return base
        start, speed, ramp = self.spin
        dt = t - start
        # Accelerate smoothly over `ramp` seconds, then turn at constant speed.
        travelled = speed * (dt * dt / (2 * ramp) if dt < ramp else dt - ramp / 2) if ramp > 0 else speed * dt
        return base - travelled  # clockwise

    def pulse_scale(self, t: float) -> float:
        if not self.pulse:
            return 1.0
        start, end, beat, amount = self.pulse
        if not start <= t <= end:
            return 1.0
        phase = ((t - start) % beat) / beat
        return 1.0 + amount * (1 - phase) ** 3


@dataclass
class Link:
    """A thin line from node `a` to node `b` that draws itself in, then may fade out."""

    a: Node
    b: Node
    color: str
    t_draw: float
    dur: float = 0.6
    width: int = 2
    gap_a: float = 0.0          # distance kept clear around a's centre (world px)
    gap_b: float = 0.0
    t_hide: float | None = None
    hide_dur: float = 0.4
    arrow: bool = False
    dash: int = 0               # dash length in px (0 = solid)
    opacity: float = 1.0
    easing: str = "ease_in_out"
    offset_a: tuple[float, float] = (0.0, 0.0)
    offset_b: tuple[float, float] = (0.0, 0.0)

    def progress(self, t: float) -> float:
        if t < self.t_draw:
            return 0.0
        return ease(self.easing, (t - self.t_draw) / max(self.dur, _EPS))

    def alpha(self, t: float) -> float:
        if self.t_hide is None or t < self.t_hide:
            return self.opacity
        return self.opacity * (1 - ease("ease_in_out", (t - self.t_hide) / max(self.hide_dur, _EPS)))


@dataclass
class Stage:
    width: int
    height: int
    duration: float
    focus: tuple[float, float]          # screen point the camera centre maps to
    camera: Camera
    background: str
    nodes: list[Node] = field(default_factory=list)
    links: list[Link] = field(default_factory=list)

    def node(self, sprite: Image.Image, x: float, y: float, **kwargs) -> Node:
        n = Node(sprite, x, y, **kwargs)
        self.nodes.append(n)
        return n

    def link(self, a: Node, b: Node, color: str, t_draw: float, **kwargs) -> Link:
        line = Link(a, b, color, t_draw, **kwargs)
        self.links.append(line)
        return line
