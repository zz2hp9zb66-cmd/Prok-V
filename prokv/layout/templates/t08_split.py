"""08 — Split Layout: a burgundy panel with the key term, the explanation below."""

from prokv.graphics import shapes
from prokv.layout.templates.base import SceneContext, template
from prokv.models import Scene


@template("split")
def build(scene: Scene, ctx: SceneContext) -> None:
    c, g, t = scene.content, ctx.grid, ctx.theme
    p = ctx.palette
    panel_h = int(g.height * 0.48)
    ctx.add(shapes.block(g.width, panel_h, p.burgundy), 0, 0, "wipe_right", start=0.0, duration=ctx.seq.dur(1.0))
    ctx.seq.wait(0.5)
    term = ctx.fit(c.headline, g.content_w, panel_h * 0.45, int(ctx.type.display * 1.35), highlights=[],
                   max_lines=2)
    term_y = panel_h - 90 - term.height
    if c.kicker:
        ctx.kicker(c.kicker, y=term_y - 80, color=p.paper)
    ctx.place_words(term, g.left, term_y, p.cream)

    y = panel_h + 110
    body = ctx.fit(c.body, g.content_w, g.bottom - y - 80, int(ctx.type.title * 0.82), highlights=c.highlights,
                   max_lines=6)
    bottom = ctx.place_words(body, g.left, y, t.foreground)
    ctx.rule(g.left, bottom + 56, 140, t.accent)
