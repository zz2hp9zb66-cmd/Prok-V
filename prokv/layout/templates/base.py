"""Shared building blocks for scene templates.

A template receives a Scene and a SceneContext and adds animated elements to the
context. SceneContext wraps the style, grid, fonts and timeline so templates only
describe *what* goes *where* and *when*.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from PIL import Image

from prokv.animation import PRESETS, Element, Motion, Sequencer
from prokv.config import VideoSpec
from prokv.graphics import shapes
from prokv.layout.grid import Grid
from prokv.models import Scene
from prokv.style import SceneTheme, VisualStyle
from prokv.typography import FontBook, TextLayout, fit_layout, label_sprite, word_sprite

TEMPLATES: dict[str, Callable[[Scene, "SceneContext"], None]] = {}


def template(kind: str):
    def register(fn):
        TEMPLATES[kind] = fn
        return fn
    return register


@dataclass
class SceneContext:
    spec: VideoSpec
    style: VisualStyle
    theme: SceneTheme
    fonts: FontBook
    index: int = 0
    total: int = 1
    duration: float = 5.0
    elements: list[Element] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.grid = Grid.for_spec(self.spec, self.style.spacing)
        self.seq = Sequencer(self.style.motion)
        self.type = self.style.type
        self.space = self.style.spacing
        self.palette = self.style.palette

    # -- generic -----------------------------------------------------------

    def motion(self, name: str | Motion) -> Motion:
        if isinstance(name, Motion):
            return name
        m = PRESETS[name]
        slide = self.style.motion.slide_px
        if m.dy and not m.mask:
            m = m.with_(dy=slide if m.dy > 0 else -slide)
        if m.dx:
            m = m.with_(dx=slide * 1.2 if m.dx > 0 else -slide * 1.2)
        return m

    def add(self, sprite: Image.Image, x: float, y: float, motion: str | Motion = "fade_up",
            start: float | None = None, duration: float | None = None, exits: bool = True,
            cls=Element, **kwargs) -> Element:
        element = cls(sprite=sprite, x=x, y=y,
                      start=self.seq.next() if start is None else start,
                      duration=self.seq.enter if duration is None else duration,
                      motion=self.motion(motion), exits=exits,
                      default_easing=self.style.motion.easing, **kwargs)
        self.elements.append(element)
        return element

    # -- typography helpers ------------------------------------------------

    def fit(self, text: str, width: float, max_height: float, size: int, role: str = "display",
            accent_role: str | None = "display_italic", highlights: list[str] | None = None,
            leading: float | None = None, align: str = "left", max_lines: int = 6) -> TextLayout:
        leading = leading or (self.type.display_leading if role.startswith("display") else self.type.body_leading)

        def fonts(sz):
            return self.fonts.get(role, sz), self.fonts.get(accent_role or role, sz)

        return fit_layout(text, fonts, width, max_height, size, int(size * self.type.min_scale),
                          max_lines=max_lines, leading=leading, highlights=highlights or [], align=align)

    def place_words(self, layout: TextLayout, x: float, y: float, color: str, accent: str | None = None,
                    motion: str = "mask_up", stagger: bool = True) -> float:
        """One element per word, revealed in sequence (kinetic typography). Returns bottom y."""
        starts = self.seq.words(len(layout.words)) if stagger else [self.seq.next()] * len(layout.words)
        for word, start in zip(layout.words, starts):
            sprite, top = word_sprite(word, layout, color, accent or self.theme.accent)
            self.add(sprite, x + word.x - (sprite.width - word.width) / 2, y + word.baseline - top, motion, start)
        return y + layout.height

    def place_lines(self, layout: TextLayout, x: float, y: float, color: str, accent: str | None = None,
                    motion: str = "fade_up", gap: float = 0.12) -> float:
        """One element per line, staggered. Returns bottom y."""
        for line_no in range(layout.lines):
            words = [w for w in layout.words if w.line == line_no]
            if not words:
                continue
            first = words[0]
            ascent, descent = layout.font.getmetrics()
            pad = int(ascent * 0.1) + 2
            width = int(words[-1].x + words[-1].width - first.x + 2 * pad)
            line = Image.new("RGBA", (max(width, 1), ascent + descent + 2 * pad), (0, 0, 0, 0))
            for w in words:
                sprite, top = word_sprite(w, layout, color, accent or self.theme.accent)
                line.alpha_composite(sprite, (int(w.x - first.x + pad - (sprite.width - w.width) / 2),
                                              int(pad + ascent - top)))
            self.add(line, x + first.x - pad, y + first.baseline - ascent - pad, motion, self.seq.next(gap))
        return y + layout.height

    def label(self, text: str, x: float, y: float, color: str | None = None, align: str = "left",
              motion: str = "fade_up", start: float | None = None) -> float:
        """Small tracked uppercase label. Returns its bottom y."""
        if not text:
            return y
        sprite = label_sprite(text, self.fonts.get("mono", self.type.label), color or self.theme.accent,
                              self.type.label_tracking)
        if align == "center":
            x -= sprite.width / 2
        elif align == "right":
            x -= sprite.width
        self.add(sprite, x, y, motion, start)
        return y + sprite.height

    def kicker(self, text: str, y: float | None = None, color: str | None = None) -> float:
        """Accent dash + label at the top of the content area. Returns the y below it."""
        y = self.grid.top if y is None else y
        if not text:
            return y
        color = color or self.theme.accent
        size = self.type.label
        dash = shapes.rule(44, self.space.rule_px, color)
        self.add(dash, self.grid.left, y + size * 0.55, "draw_right", self.seq.next(0.1))
        bottom = self.label(text, self.grid.left + 64, y, color)
        return bottom + self.space.gap

    def rule(self, x: float, y: float, length: int, color: str | None = None, vertical: bool = False,
             thickness: int | None = None, motion: str | None = None, start: float | None = None,
             duration: float | None = None) -> Element:
        sprite = shapes.rule(int(length), thickness or self.space.rule_px, color or self.theme.accent, vertical)
        return self.add(sprite, x, y, motion or ("draw_down" if vertical else "draw_right"), start, duration)
