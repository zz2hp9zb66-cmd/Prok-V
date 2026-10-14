"""Documentary Reels: scene library and builder.

Visual types: decade_counter, rough_wave, sampling, europe_map, voice_wave,
split, flow, autotune, formats, finale.
"""

from __future__ import annotations

from PIL import Image

from prokv.animation.stage import Camera, Stage
from prokv.config import VideoSpec
from prokv.layout.documentary import visuals  # noqa: F401  (registers visual types)
from prokv.layout.documentary.base import (
    VISUALS, DocKit, SceneContext, decade_timeline, fact_box, music_cards, scene_title,
)
from prokv.style import DEFAULT_STYLE, VisualStyle

FOCUS = (540, 900)


def build_documentary(doc, style: VisualStyle = DEFAULT_STYLE, spec: VideoSpec = VideoSpec()):
    """Documentary -> (Stage, overlay) for StageRenderer."""
    kit = DocKit(style)
    stage = Stage(spec.width, spec.height, doc.duration, FOCUS, Camera(*FOCUS), kit.t.background)
    decade_timeline(stage, kit, doc)
    for i, scene in enumerate(doc.scenes):
        ctx = SceneContext(stage, kit, doc, scene, i)
        scene_title(ctx)
        VISUALS[scene.visual["type"]](ctx)
        if scene.visual["type"] != "split":     # split places its cards inside the halves
            music_cards(ctx)
        fact_box(ctx)
        ctx.finish()
    return stage, _overlay(kit, doc)


def _overlay(kit: DocKit, doc):
    """Thin progress line and the final fade-out."""
    sp = kit.style.spacing
    dark = None

    def overlay(frame: Image.Image, t: float) -> None:
        nonlocal dark
        x0, x1 = sp.margin_x, frame.width - sp.margin_x
        y = sp.footer_y
        frame.paste(kit.olive, (x0, y, x1, y + 1))
        filled = x0 + int((x1 - x0) * min(t / doc.duration, 1.0))
        if filled > x0:
            frame.paste(kit.paper, (x0, y - 1, filled, y + 2))
        fade = (t - (doc.duration - 0.7)) / 0.7
        if fade > 0:
            dark = dark or Image.new("RGB", frame.size, kit.p.dark_burgundy)
            frame.paste(Image.blend(frame, dark, min(fade, 1.0)))

    return overlay


__all__ = ["VISUALS", "build_documentary"]
