"""03 — Comparison: two sides divided by a drawn line."""

from prokv.graphics import shapes
from prokv.layout.templates.base import SceneContext, template
from prokv.models import Scene
from prokv.typography import text_sprite


@template("comparison")
def build(scene: Scene, ctx: SceneContext) -> None:
    c, g, t = scene.content, ctx.grid, ctx.theme
    y = ctx.kicker(c.kicker)
    if c.headline:
        head = ctx.fit(c.headline, g.content_w, 260, ctx.type.title, highlights=[], max_lines=2)
        y = ctx.place_words(head, g.left, y, t.foreground)
    top = y + 110
    gutter = 150
    col_w = (g.content_w - gutter) / 2
    divider_x = g.left + col_w + gutter / 2
    sides = (c.pairs + [["", ""], ["", ""]])[:2]
    layouts = [ctx.fit(text, col_w, (g.bottom - top) * 0.7, int(ctx.type.subtitle * 1.3),
                       highlights=c.highlights if i == 1 else [], max_lines=7)
               for i, (_, text) in enumerate(sides)]
    text_top = top + 70
    bottom = text_top + max(l.height for l in layouts) + 110

    ctx.rule(divider_x - 1, top, int(bottom - top), t.line, vertical=True, thickness=ctx.space.hairline_px,
             start=ctx.seq.next(0.1), duration=ctx.seq.dur(1.2))
    d = 92
    badge = shapes.circle(d, ctx.theme.background)
    badge.alpha_composite(shapes.circle(d, t.line, outline=ctx.space.hairline_px))
    vs = text_sprite("vs", ctx.fonts.get("serif_italic", 40), t.muted)
    badge.alpha_composite(vs, (int((d - vs.width) / 2), int((d - vs.height) / 2) - 2))
    ctx.add(badge, divider_x - d / 2, (top + bottom) / 2 - d / 2, "scale_in", start=ctx.seq.next())

    for i, ((label, _), layout) in enumerate(zip(sides, layouts)):
        x = g.left if i == 0 else divider_x + gutter / 2
        color = t.muted if i == 0 else t.foreground
        motion = "fade_right" if i == 0 else "fade_left"
        ctx.label(label, x, top, t.muted if i == 0 else t.accent, motion=motion)
        text_bottom = ctx.place_lines(layout, x, text_top, color, motion=motion)
        ctx.rule(x, text_bottom + 40, 90, t.muted if i == 0 else t.accent)
