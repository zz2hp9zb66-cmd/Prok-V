"""04 — List: numbered rows separated by drawn hairlines."""

from prokv.layout.templates.base import SceneContext, template
from prokv.models import Scene


@template("list")
def build(scene: Scene, ctx: SceneContext) -> None:
    c, g, t = scene.content, ctx.grid, ctx.theme
    y = ctx.kicker(c.kicker)
    if c.headline:
        head = ctx.fit(c.headline, g.content_w, 300, ctx.type.title, highlights=c.highlights, max_lines=3)
        y = ctx.place_words(head, g.left, y, t.foreground) + 80
    items = c.items[:5]
    row_h = min(230, (g.bottom - y) / max(len(items), 1))
    indent = 120
    for i, item in enumerate(items):
        row_y = y + i * row_h
        ctx.rule(g.left, row_y, g.content_w, t.line, thickness=ctx.space.hairline_px, start=ctx.seq.next(0.05),
                 duration=ctx.seq.dur(0.8))
        ctx.label(f"{i + 1:02d}", g.left, row_y + 34, t.accent, start=ctx.seq.next(0.05))
        layout = ctx.fit(item, g.content_w - indent, row_h - 50, ctx.type.subtitle, role="display",
                         highlights=[], max_lines=2)
        ctx.place_lines(layout, g.left + indent, row_y + 22, t.foreground, gap=0.3)
    ctx.rule(g.left, y + len(items) * row_h, g.content_w, t.line, thickness=ctx.space.hairline_px,
             duration=ctx.seq.dur(0.8))
