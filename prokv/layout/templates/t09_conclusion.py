"""09 — Conclusion: the takeaway, centred under a vinyl record."""

from prokv.graphics import shapes
from prokv.layout.templates.base import SceneContext, template
from prokv.models import Scene


@template("conclusion")
def build(scene: Scene, ctx: SceneContext) -> None:
    c, g, t = scene.content, ctx.grid, ctx.theme
    p = ctx.palette
    d = int(g.content_w * 0.56)
    record = shapes.vinyl(d, p.warm_black, p.espresso, p.burgundy, t.background)
    ctx.add(record, g.center_x - d / 2, g.top, "scale_in", start=ctx.seq.next(), duration=ctx.seq.dur(1.4))
    y = g.top + d + 70
    y = ctx.label(c.kicker, g.center_x, y, t.accent, align="center") + ctx.space.gap
    head = ctx.fit(c.headline, g.content_w, g.bottom - y - 120, ctx.type.title, highlights=c.highlights,
                   align="center", max_lines=5)
    bottom = ctx.place_words(head, g.left, y, t.foreground)
    if c.body:
        body = ctx.fit(c.body, g.content_w, 160, ctx.type.body, role="text", accent_role=None, align="center")
        bottom = ctx.place_lines(body, g.left, bottom + ctx.space.gap, t.muted)
    ctx.rule(g.center_x - 50, bottom + 56, 100, t.accent)
