"""06 — Quote: italic serif quotation on a dark ground, oversized quote mark."""

from prokv.graphics import shapes
from prokv.layout.templates.base import SceneContext, template
from prokv.models import Scene


@template("quote")
def build(scene: Scene, ctx: SceneContext) -> None:
    c, g, t = scene.content, ctx.grid, ctx.theme
    y = ctx.kicker(c.kicker)
    mark = shapes.quote_mark(ctx.fonts.get("display", 380), ctx.palette.burgundy)
    ctx.add(mark, g.left - 18, y - 40, "scale_in", start=ctx.seq.next(), duration=ctx.seq.dur(1.4))
    quote = f"«{c.quote}»" if not c.quote.startswith(("«", "“", '"')) else c.quote
    layout = ctx.fit(quote, g.content_w, g.content_h * 0.55, int(ctx.type.title * 1.02), role="display_italic",
                     accent_role=None, max_lines=8)
    qy = max(y + 220, g.top + (g.content_h - layout.height) * 0.45)
    bottom = ctx.place_lines(layout, g.left, qy, t.foreground, motion="mask_up", gap=0.22)
    if c.author:
        ctx.rule(g.left, bottom + 70, 80, t.accent)
        ctx.label(c.author, g.left, bottom + 110, t.muted)
