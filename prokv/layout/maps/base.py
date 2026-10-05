"""Shared machinery for "Карта одного трека" sections.

An episode is a list of timed sections (hook, object, coordinates, ...). Each
section is a function registered with @section("name") that adds nodes and
links to the Stage through a MapContext. The central object (sleeve, vinyl,
title) persists across sections and is posed by them via `ctx.center`.

Lifecycle: nodes/links a section creates are "transient": they fade out at the
end of the section, unless the section has `"keep": true` — then they are
handed to the next section, which can take them over (`ctx.take_carried()`),
otherwise they fade out as it starts.
"""

from __future__ import annotations

import re
from typing import Callable

from PIL import Image

from prokv.animation.stage import Link, Node, Stage
from prokv.content.track_map import Episode, Section
from prokv.graphics import objects, shapes
from prokv.style import VisualStyle
from prokv.typography import FontBook, label_sprite, text_sprite

SECTIONS: dict[str, Callable[["MapContext", Section], None]] = {}


def section(name: str):
    def register(fn):
        SECTIONS[name] = fn
        return fn
    return register


class Kit:
    """Sprite factory bound to the style."""

    def __init__(self, style: VisualStyle) -> None:
        self.style = style
        self.fonts = FontBook(style.fonts)
        self.p = style.palette
        self.t = style.themes["cream"]

    def text(self, text: str, size: int, color: str | None = None, role: str = "display") -> Image.Image:
        return text_sprite(text, self.fonts.get(role, size), color or self.t.foreground)

    def label(self, text: str, size: int = 24, color: str | None = None, tracking: int = 5) -> Image.Image:
        return label_sprite(text, self.fonts.get("mono", size), color or self.t.accent, tracking)

    def fit(self, lines: list[str], max_size: int, max_w: float, role: str = "display") -> int:
        size = max_size
        while size > 18 and max(self.fonts.get(role, size).getlength(l) for l in lines) > max_w:
            size -= 2
        return size

    def lines(self, text: str, size: int, max_w: float, role: str = "display") -> list[str]:
        font = self.fonts.get(role, size)
        out, cur = [], ""
        for word in text.split():
            cand = f"{cur} {word}".strip()
            if cur and font.getlength(cand) > max_w:
                out.append(cur)
                cur = word
            else:
                cur = cand
        return out + ([cur] if cur else [])

    def wrap(self, text: str, size: int, max_w: float, color: str | None = None, role: str = "display",
             align: str = "center", leading: float = 1.12) -> Image.Image:
        sprites = [self.text(l, size, color, role) for l in self.lines(text, size, max_w, role)]
        return self.stack(sprites, align, int(size * (leading - 1.0)) - 8)

    def wrap_fit(self, text: str, max_size: int, max_w: float, max_lines: int, role: str = "display") -> int:
        size = max_size
        while size > 22 and (len(self.lines(text, size, max_w, role)) > max_lines
                             or any(self.fonts.get(role, size).getlength(w) > max_w for w in text.split())):
            size -= 2
        return size

    @staticmethod
    def stack(sprites: list[Image.Image], align: str = "center", gap: int = 6) -> Image.Image:
        w = max(s.width for s in sprites)
        h = sum(s.height for s in sprites) + gap * (len(sprites) - 1)
        out = Image.new("RGBA", (w, max(h, 1)), (0, 0, 0, 0))
        y = 0
        for s in sprites:
            x = {"left": 0, "right": w - s.width}.get(align, (w - s.width) // 2)
            out.alpha_composite(s, (x, y))
            y += s.height + gap
        return out

    def info(self, label: str, value: str, align: str = "center", value_size: int = 46,
             max_w: float = 10_000) -> Image.Image:
        value_sprite = self.wrap(value, value_size, max_w, align=align, leading=1.05)
        return self.stack([self.label(label), value_sprite], align)

    def dot(self, d: int = 14, color: str | None = None) -> Image.Image:
        return shapes.dot(d, color or self.t.accent)


def left_x(sprite: Image.Image, x: float) -> float:
    return x + sprite.width / 2


def right_x(sprite: Image.Image, x: float) -> float:
    return x - sprite.width / 2


def edge_gap(sprite: Image.Image, dx: float, dy: float, pad: float = 18) -> float:
    """Distance from a sprite's centre to its box edge in direction (dx, dy), plus padding."""
    length = (dx * dx + dy * dy) ** 0.5 or 1.0
    ux, uy = abs(dx) / length, abs(dy) / length
    hw, hh = sprite.width / 2, sprite.height / 2
    return min(hw / ux if ux > 1e-6 else 1e9, hh / uy if uy > 1e-6 else 1e9) + pad


def is_year(text: str) -> bool:
    return bool(re.fullmatch(r"\d{4}s?|\d{2}s|\d{4}[–-]\d{2,4}", text.strip()))


class Center:
    """The persistent central object: sleeve + vinyl + title, plus an invisible hub."""

    def __init__(self, ctx: "MapContext") -> None:
        k, st, ep = ctx.kit, ctx.stage, ctx.ep
        cover = Image.open(ep.cover_image) if ep.cover_image else None
        self.vinyl = st.node(objects.vinyl_record(420, k.p), 540, 900, z=1)
        self.sleeve = st.node(objects.sleeve(400, k.p, ep.sleeve_title or ep.album, ep.artist,
                                              f"{ep.label} · {ep.year}", k.fonts, cover), 500, 900, z=2)
        title = ep.track.upper()
        self.title = st.node(k.text(title, k.fit([title], 150, 920)), 540, 1190, z=5)
        self.hub = st.node(k.dot(2), 540, 900)
        self.visible = {self.vinyl: False, self.sleeve: False, self.title: False}

    def place(self, node: Node, t: float, dur: float, visible: bool, easing: str = "ease_in_out",
              show: dict | None = None, **props) -> None:
        was = self.visible[node]
        t = max(t, node.keys[-1].t)
        if visible and not was:
            node.set(t, **props)
            node.show(t, **({"dur": dur, "dy": 0, "scale_from": 0.9} | (show or {})))
        elif visible:
            node.animate(t, dur, easing, opacity=1.0, **props)
        elif was:
            node.hide(t, min(dur, 0.45), dy=0)
        self.visible[node] = visible

    def pose(self, t: float, dur: float, mode: str, cx: float = 540, cy: float = 900, s: float = 1.0,
             title_scale: float | None = None, title_y: float | None = None, vinyl_y: float | None = None,
             vinyl_scale: float | None = None, show: dict | None = None) -> None:
        """Modes: vinyl | object | title | hidden."""
        v, sl, ti = self.vinyl, self.sleeve, self.title
        if mode == "vinyl":
            self.place(v, t, dur, True, x=cx, y=cy, scale=s, show=show)
            self.place(sl, t, dur, False)
            self.place(ti, t, dur, False)
        elif mode == "object":
            self.place(v, t, dur, True, x=cx + 74 * s, y=cy, scale=0.92 * s)
            self.place(sl, t, dur, True, x=cx - 66 * s, y=cy, scale=s, show=show)
            self.place(ti, t, dur, True, x=cx, y=title_y or cy + 200 * s + 50,
                       scale=title_scale or 0.68 * s, show={"rise": True, "dur": 0.85})
        elif mode == "title":
            self.place(sl, t, dur, False)
            self.place(v, t, dur, True, x=cx, y=vinyl_y or cy - 80, scale=vinyl_scale or 0.3)
            self.place(ti, t, dur, True, x=cx, y=title_y or cy + 50, scale=title_scale or 0.5)
        else:
            for node in (v, sl, ti):
                self.place(node, t, dur, False)
        hub_t = max(t, self.hub.keys[-1].t)
        self.hub.animate(hub_t, dur, "ease_in_out", x=cx, y=cy)

    def dim(self, t: float, opacity: float, dur: float = 0.5) -> None:
        for node, vis in self.visible.items():
            if vis:
                node.animate(max(t, node.keys[-1].t), dur, "ease_in_out", opacity=opacity)


class MapContext:
    def __init__(self, ep: Episode, stage: Stage, kit: Kit) -> None:
        self.ep = ep
        self.stage = stage
        self.kit = kit
        self.beat = 60.0 / ep.bpm
        self.named: dict[str, object] = {}
        self.transient: list[Node | Link] = []
        self.carried: list[Node | Link] = []
        self.center = Center(self)

    # -- creation ------------------------------------------------------------

    def node(self, sprite: Image.Image, x: float, y: float, z: int = 4, fixed: bool = False) -> Node:
        n = self.stage.node(sprite, x, y, z=z, fixed=fixed)
        self.transient.append(n)
        return n

    def anchor(self, x: float, y: float) -> Node:
        return self.stage.node(self.kit.dot(2), x, y)

    def link(self, a: Node, b: Node, color: str | None, t: float, **kwargs) -> Link:
        line = self.stage.link(a, b, color or self.kit.t.line, t, **kwargs)
        self.transient.append(line)
        return line

    # -- lifecycle -----------------------------------------------------------

    def take_carried(self) -> list[Node | Link]:
        items, self.carried = self.carried, []
        self.transient.extend(items)
        return items

    @staticmethod
    def fade(items, t: float, dur: float = 0.42) -> None:
        for item in items:
            if isinstance(item, Link):
                item.t_hide = t if item.t_hide is None else min(item.t_hide, t)
                item.hide_dur = dur
            elif item.value(1e9)["opacity"] > 0:
                item.hide(max(t, item.keys[-1].t), dur, dy=0)

    def begin(self, sec: Section) -> None:
        # Carried items the new section does not take over fade out as it starts.
        self._pending = self.carried

    def end(self, sec: Section) -> None:
        if self._pending and self._pending is self.carried:
            self.fade(self.carried, sec.start - 0.15)
            self.carried = []
        if sec.data.get("keep"):
            self.carried = self.transient
        else:
            self.fade(self.transient, sec.end - 0.45)
        self.transient = []
