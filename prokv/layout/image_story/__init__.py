"""Photo-led documentary Reels: scene layouts and the builder.

Layouts: hook, camera, designer, formula, system, legacy, finale.
"""

from __future__ import annotations

from PIL import Image

from prokv.animation.stage import Camera, Stage
from prokv.config import VideoSpec
from prokv.layout.image_story import scenes  # noqa: F401  (registers layouts)
from prokv.layout.image_story.base import LAYOUTS, StoryContext, StoryKit, TextRecord, auto_fixes, check_text_bounds

FOCUS = (540, 900)


def build_story(story, timing: list[tuple[float, float]], spec: VideoSpec = VideoSpec()):
    """Story + final (start, end) per scene -> (Stage, overlay, text records)."""
    kit = StoryKit(story.palette)
    duration = timing[-1][1]
    stage = Stage(spec.width, spec.height, duration, FOCUS, Camera(*FOCUS), kit.cream)
    texts: list[TextRecord] = []
    for i, (scene, (s, e)) in enumerate(zip(story.scenes, timing)):
        ctx = StoryContext(stage, kit, story, scene, s, e, i, texts)
        LAYOUTS[scene.layout](ctx)
        ctx.finish()
        if i:  # editorial transition: a blue bar sweeps across at each cut
            bar = stage.node(kit.block(260, spec.height, kit.blue), -200, spec.height / 2, z=9)
            bar.set(s - 0.45, opacity=1.0)
            bar.animate(s - 0.45, 0.8, "ease_in_out", x=spec.width + 200)
    return stage, _overlay(kit, duration), texts


def _overlay(kit: StoryKit, duration: float):
    dark = None

    def overlay(frame: Image.Image, t: float) -> None:
        nonlocal dark
        fade = (t - (duration - 0.8)) / 0.8
        if fade > 0:
            dark = dark or Image.new("RGB", frame.size, kit.ink)
            frame.paste(Image.blend(frame, dark, min(fade, 1.0)))

    return overlay


__all__ = ["LAYOUTS", "auto_fixes", "build_story", "check_text_bounds"]
