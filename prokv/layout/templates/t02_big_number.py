"""02 — Big Number: a key figure, counted up.

Default: a ring chart for percentages. Variant "alt" (or non-percent numbers):
the number set huge and left-aligned over an accent rule.
"""

from prokv.animation import CounterElement, Element
from prokv.content.text import find_numbers
from prokv.graphics import shapes
from prokv.layout.templates.base import SceneContext, template
from prokv.models import Scene
from prokv.typography import text_sprite


@template("big_number")
def build(scene: Scene, ctx: SceneContext) -> None:
    c, g, t = scene.content, ctx.grid, ctx.theme
    y = ctx.kicker(c.kicker)
    numbers = find_numbers(c.number)
    percent = (scene.variant != "alt" and c.number.rstrip().endswith("%") and numbers
               and 0 < numbers[0].value <= 100)
    count = ctx.style.motion.count_up and bool(numbers)

    def number_sprite(size, text):
        return text_sprite(text, ctx.fonts.get("display", size), t.foreground)

    if percent:
        d = int(g.content_w * 0.78)
        ring_y = y + 20
        cx = g.center_x
        stroke = 10
        ctx.add(shapes.ring(d, 2, t.line), cx - d / 2, ring_y, "fade", start=ctx.seq.next(0))
        start = ctx.seq.next(0)
        long = ctx.seq.dur(1.8)
        ctx.add(shapes.ring(d, stroke, t.accent, extent=360 * numbers[0].value / 100), cx - d / 2, ring_y,
                "draw_radial", start=start, duration=long)
        size = ctx.type.hero
        while ctx.fonts.get("display", size).getlength(c.number) > d * 0.66 and size > 80:
            size -= 8
        final = number_sprite(size, c.number)
        extra = {"render": lambda s: number_sprite(size, s), "text": c.number, "align": "center"} if count else {}
        ctx.add(final, cx - final.width / 2, ring_y + (d - final.height) / 2, "fade", start=start,
                duration=long, cls=CounterElement if count else Element, **extra)
        y = ring_y + d + 70
        align, x, width = "center", g.left, g.content_w
    else:
        size = ctx.type.hero
        while ctx.fonts.get("display", size).getlength(c.number) > g.content_w and size > 80:
            size -= 8
        final = number_sprite(size, c.number)
        start = ctx.seq.next()
        extra = {"render": lambda s: number_sprite(size, s), "text": c.number, "align": "left"} if count else {}
        ctx.add(final, g.left - 4, y + 40, "mask_up", start=start, duration=ctx.seq.dur(1.4),
                cls=CounterElement if count else Element, **extra)
        y += 40 + final.height + 20
        ctx.rule(g.left, y, 160, t.accent)
        y += ctx.space.gap + 10
        align, x, width = "left", g.left, g.content_w

    head = ctx.fit(c.headline, width, 300, ctx.type.title * 0.78, highlights=c.highlights, align=align, max_lines=3)
    y = ctx.place_words(head, x, y, t.foreground) + ctx.space.gap * 0.6
    if c.body:
        body = ctx.fit(c.body, width, 200, ctx.type.body, role="text", accent_role=None, align=align)
        ctx.place_lines(body, x, y, t.muted)
