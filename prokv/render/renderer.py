"""Storyboard -> frames. Builds each scene from its template, then composes frames:
paper background, header chrome, animated elements, scene-to-scene transitions.
"""

from __future__ import annotations

import bisect
from dataclasses import dataclass
from typing import Iterator

from PIL import Image

from prokv.animation.easing import ease
from prokv.graphics.texture import paper
from prokv.layout.templates import TEMPLATES, SceneContext
from prokv.models import Storyboard
from prokv.style import DEFAULT_STYLE, SceneTheme, VisualStyle
from prokv.typography import FontBook, label_sprite


@dataclass
class BuiltScene:
    start: float
    duration: float
    theme: SceneTheme
    context: SceneContext
    background: Image.Image
    chrome: Image.Image | None


class StoryboardRenderer:
    def __init__(self, storyboard: Storyboard, style: VisualStyle = DEFAULT_STYLE) -> None:
        self.storyboard = storyboard
        self.spec = storyboard.spec
        self.style = style
        self.fonts = FontBook(style.fonts)
        self.size = (self.spec.width, self.spec.height)
        self.scenes: list[BuiltScene] = []
        t = 0.0
        for i, scene in enumerate(storyboard.scenes):
            if scene.kind not in TEMPLATES:
                raise ValueError(f"Unknown scene kind {scene.kind!r}. Available: {', '.join(TEMPLATES)}")
            theme = style.theme_for(scene.kind)
            ctx = SceneContext(self.spec, style, theme, self.fonts, i, len(storyboard.scenes), scene.duration_s)
            TEMPLATES[scene.kind](scene, ctx)
            background = paper(self.size, theme.background, style.grain)
            self.scenes.append(BuiltScene(t, scene.duration_s, theme, ctx, background, self._chrome(i, theme)))
            t += scene.duration_s
        self.duration = t
        self._starts = [s.start for s in self.scenes]

    @property
    def frame_count(self) -> int:
        return max(1, round(self.duration * self.spec.fps))

    def frames(self) -> Iterator[Image.Image]:
        for i in range(self.frame_count):
            yield self.render(i / self.spec.fps)

    def render(self, t: float) -> Image.Image:
        i = max(0, bisect.bisect_right(self._starts, t) - 1)
        scene = self.scenes[i]
        local = t - scene.start
        motion = self.style.motion
        last = i == len(self.scenes) - 1
        trans = 0.0 if last or motion.transition == "cut" else min(motion.transition_s / motion.speed,
                                                                     scene.duration * 0.3)
        exit_s = motion.exit_s / motion.speed

        frame = scene.background.copy()
        if scene.chrome:
            fade_in = min(1.0, local / 0.4) if i > 0 else min(1.0, local / 0.6)
            self._paste(frame, scene.chrome, fade_in)

        # Whole composition drifts slowly upwards during the scene.
        drift = -motion.drift_px * ease("ease_in_out_sine", local / scene.duration)
        exit_p = 0.0
        if not last:
            exit_start = scene.duration - trans - exit_s * 0.6
            exit_p = ease("ease_in", (local - exit_start) / exit_s) if local > exit_start else 0.0
        for element in scene.context.elements:
            element.draw(frame, local, (0, drift), exit_p, exit_dy=motion.slide_px * 0.6)

        if trans and local > scene.duration - trans:
            p = ease("ease_in_out", (local - (scene.duration - trans)) / trans)
            nxt = self.scenes[i + 1]
            if motion.transition == "fade":
                frame = Image.blend(frame, nxt.background, p)
            else:  # wipe_up: next background rises from the bottom edge
                top = int(self.spec.height * (1 - p))
                if top < self.spec.height:
                    frame.paste(nxt.background.crop((0, top, self.spec.width, self.spec.height)), (0, top))
        if self.style.show_progress:
            self._progress(frame, t, scene.theme)
        return frame

    # -- chrome ------------------------------------------------------------

    def _chrome(self, index: int, theme: SceneTheme) -> Image.Image | None:
        if not self.style.show_header:
            return None
        sp, ty = self.style.spacing, self.style.type
        chrome = Image.new("RGBA", self.size, (0, 0, 0, 0))
        font = self.fonts.get("mono", int(ty.label * 0.85))
        counter = label_sprite(f"{index + 1:02d} / {len(self.storyboard.scenes):02d}", font, theme.line,
                               ty.label_tracking)
        chrome.alpha_composite(counter, (sp.margin_x, sp.header_y))
        title = self.storyboard.title
        right_edge = self.spec.width - sp.margin_x
        while title:
            label = label_sprite(title, font, theme.line, ty.label_tracking)
            if label.width <= right_edge - sp.margin_x - counter.width - 60:
                chrome.alpha_composite(label, (right_edge - label.width, sp.header_y))
                break
            title = title.rsplit(" ", 1)[0] if " " in title else ""
        rule_y = sp.header_y + counter.height + 18
        chrome.paste(theme.line, (sp.margin_x, rule_y, right_edge, rule_y + sp.hairline_px - 1 + 1))
        return chrome

    def _progress(self, frame: Image.Image, t: float, theme: SceneTheme) -> None:
        sp = self.style.spacing
        x0, x1 = sp.margin_x, self.spec.width - sp.margin_x
        y = sp.footer_y
        frame.paste(theme.line, (x0, y, x1, y + 1))
        filled = x0 + int((x1 - x0) * min(t / self.duration, 1.0))
        if filled > x0:
            frame.paste(theme.accent, (x0, y - 1, filled, y + 2))

    @staticmethod
    def _paste(frame: Image.Image, image: Image.Image, opacity: float) -> None:
        alpha = image.getchannel("A")
        if opacity < 0.997:
            alpha = alpha.point(lambda v: int(v * opacity))
        frame.paste(image, (0, 0), alpha)
