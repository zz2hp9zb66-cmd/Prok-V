"""07 — Diagram: steps in frames connected by arrows; the last step is the result."""

from prokv.graphics import shapes
from prokv.layout.templates.base import SceneContext, template
from prokv.models import Scene


@template("diagram")
def build(scene: Scene, ctx: SceneContext) -> None:
    c, g, t = scene.content, ctx.grid, ctx.theme
    y = ctx.kicker(c.kicker)
    if c.headline:
        head = ctx.fit(c.headline, g.content_w, 240, ctx.type.title, highlights=c.highlights, max_lines=2)
        y = ctx.place_words(head, g.left, y, t.foreground) + 80
    steps = c.items[:4]
    arrow_gap = 96
    box_h = min(230, ((g.bottom - y) - arrow_gap * (len(steps) - 1)) / max(len(steps), 1))
    for i, step in enumerate(steps):
        by = y + i * (box_h + arrow_gap)
        last = i == len(steps) - 1
        if last:
            box = shapes.block(g.content_w, int(box_h), t.accent)
            text_color, index_color = t.background, t.background
        else:
            box = shapes.frame(g.content_w, int(box_h), t.line, ctx.space.hairline_px)
            text_color, index_color = t.foreground, t.accent
        ctx.add(box, g.left, by, "wipe_right" if last else "fade", start=ctx.seq.next(0.1),
                duration=ctx.seq.dur(0.9))
        ctx.label(f"{i + 1:02d}", g.left + 36, by + 30, index_color, start=ctx.seq.next(0.05))
        layout = ctx.fit(step, g.content_w - 72, box_h - 90, int(ctx.type.subtitle * 0.95), highlights=[],
                         max_lines=2)
        ctx.place_lines(layout, g.left + 36, by + 76, text_color, gap=0.2)
        if not last:
            arrow = shapes.arrow(arrow_gap - 28, t.accent, thickness=3, head=14)
            ctx.add(arrow, g.center_x - arrow.width / 2, by + box_h + 14, "draw_down", start=ctx.seq.next(0.25),
                    duration=ctx.seq.dur(0.6))
