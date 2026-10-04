"""01 — Statement: one strong thought in large serif type."""

from prokv.graphics import shapes
from prokv.layout.templates.base import SceneContext, template
from prokv.models import Scene


@template("statement")
def build(scene: Scene, ctx: SceneContext) -> None:
    c, g, t = scene.content, ctx.grid, ctx.theme
    # Decorative thin circle, half off-canvas: drawn around like a record groove.
    d = int(g.width * 0.68)
    ctx.add(shapes.circle(d, t.line, outline=ctx.space.hairline_px), g.width - d * 0.62, g.top - 40,
            "draw_radial", start=0.0, duration=ctx.seq.dur(2.2))

    y = ctx.kicker(c.kicker)
    layout = ctx.fit(c.headline, g.content_w, g.content_h * 0.55, int(ctx.type.display * 1.25), highlights=c.highlights,
                     max_lines=5)
    body = ctx.fit(c.body, g.content_w * 0.86, 360, ctx.type.body, role="text", accent_role=None) if c.body else None
    block_h = layout.height + (60 + ctx.space.gap + body.height if body else 0)
    y = max(y, g.top + (g.content_h - block_h) * 0.42)

    bottom = ctx.place_words(layout, g.left, y, t.foreground)
    ctx.rule(g.left, bottom + 44, 140)
    if body:
        ctx.place_lines(body, g.left, bottom + 44 + ctx.space.gap, t.muted)
