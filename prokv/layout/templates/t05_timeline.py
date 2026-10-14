"""05 — Timeline: a vertical line drawing down through dated events."""

from prokv.graphics import shapes
from prokv.layout.templates.base import SceneContext, template
from prokv.models import Scene


@template("timeline")
def build(scene: Scene, ctx: SceneContext) -> None:
    c, g, t = scene.content, ctx.grid, ctx.theme
    y = ctx.kicker(c.kicker)
    if c.headline:
        head = ctx.fit(c.headline, g.content_w, 240, ctx.type.title, highlights=c.highlights, max_lines=2)
        y = ctx.place_words(head, g.left, y, t.foreground) + 90
    pairs = c.pairs[:5]
    step = min(270, (g.bottom - y) / max(len(pairs), 1))
    line_x = g.left + 12
    dot = 26
    total = ctx.seq.dur(0.55) * len(pairs)
    ctx.rule(line_x - 1, y + dot / 2, int(step * (len(pairs) - 1) + 30), t.line, vertical=True,
             thickness=ctx.space.hairline_px, start=ctx.seq.t, duration=total + ctx.seq.dur(0.4))
    year_font = int(ctx.type.title * 0.86)
    for i, (year, text) in enumerate(pairs):
        ey = y + i * step
        ctx.add(shapes.dot(dot, t.accent), line_x - dot / 2, ey, "scale_in", start=ctx.seq.next(0.08))
        year_layout = ctx.fit(year, g.content_w - 80, 120, year_font, highlights=[], max_lines=1)
        ctx.place_words(year_layout, g.left + 64, ey - year_layout.height * 0.38, t.accent)
        body = ctx.fit(text, g.content_w - 64, step - year_layout.height - 20, ctx.type.body, role="text",
                       accent_role=None, max_lines=2)
        ctx.place_lines(body, g.left + 64, ey - year_layout.height * 0.38 + year_layout.height + 6,
                        t.foreground, gap=0.25)
