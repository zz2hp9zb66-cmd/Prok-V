"""Section library for the "Карта одного трека" series and the episode builder.

Section types: hook, object, coordinates, places, branches, musicians, core,
statement, chain, cycle, afterlife, awards, final_map, outro.
"""

from __future__ import annotations

from PIL import Image

from prokv.animation.stage import Camera, Stage
from prokv.config import VideoSpec
from prokv.layout.maps import finale, intro, people, place, story  # noqa: F401  (register sections)
from prokv.layout.maps.base import SECTIONS, Kit, MapContext
from prokv.style import DEFAULT_STYLE, VisualStyle

FOCUS = (540, 900)


def build_episode(ep, style: VisualStyle = DEFAULT_STYLE, spec: VideoSpec = VideoSpec()):
    """Episode -> (Stage, overlay) for StageRenderer."""
    kit = Kit(style)
    stage = Stage(spec.width, spec.height, ep.duration, FOCUS, Camera(*FOCUS), kit.t.background)
    ctx = MapContext(ep, stage, kit)
    for i, sec in enumerate(ep.sections):
        ctx.begin(sec)
        SECTIONS[sec.type](ctx, sec)
        if i == len(ep.sections) - 1:
            ctx.carried, ctx._pending = [], None  # the last section stays on screen to the end
            ctx.transient = []
        else:
            ctx.end(sec)
    return stage, _chrome(kit, ep, spec)


def _chrome(k: Kit, ep, spec: VideoSpec):
    """Fixed header (series + episode) between the hook and the outro, and a progress line."""
    sp = k.style.spacing
    th = k.t
    header = Image.new("RGBA", (spec.width, 260), (0, 0, 0, 0))
    left = k.label(ep.series, 20, th.line, 5)
    right = k.label(f"№{ep.number:03d} / {ep.track}", 20, th.line, 5)
    header.alpha_composite(left, (sp.margin_x, sp.header_y))
    header.alpha_composite(right, (spec.width - sp.margin_x - right.width, sp.header_y))
    y = sp.header_y + left.height + 16
    header.paste(th.line, (sp.margin_x, y, spec.width - sp.margin_x, y + 1))
    alpha = header.getchannel("A")
    start = next((sec.start for sec in ep.sections if sec.type != "hook"), 0.0) + 0.2
    end = next((sec.start for sec in ep.sections if sec.type == "outro"), ep.duration)

    def overlay(frame: Image.Image, t: float) -> None:
        o = min(1.0, max(0.0, (t - start) / 0.6), max(0.0, (end - t) / 0.5))
        if o > 0.003:
            frame.paste(header, (0, 0), alpha if o >= 0.997 else alpha.point(lambda v: int(v * o)))
        x0, x1 = sp.margin_x, spec.width - sp.margin_x
        frame.paste(th.line, (x0, sp.footer_y, x1, sp.footer_y + 1))
        filled = x0 + int((x1 - x0) * min(t / ep.duration, 1.0))
        if filled > x0:
            frame.paste(th.accent, (x0, sp.footer_y - 1, filled, sp.footer_y + 2))

    return overlay


__all__ = ["SECTIONS", "build_episode"]
