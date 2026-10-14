"""hook · object"""

from __future__ import annotations

import math

from prokv.graphics import objects
from prokv.layout.maps.base import MapContext, section
from prokv.content.track_map import Section


@section("hook")
def hook(ctx: MapContext, sec: Section) -> None:
    """Big opening line(s) + optional body / question, with a small object.

    data: text | lines, body?, question?, object: "vinyl" | "helmets" | "none"
    """
    k, d, s = ctx.kit, sec.data, sec.start
    th = k.t
    obj = d.get("object", "vinyl")
    obj_y = d.get("object_y", 930 if d.get("text") else 900)
    if "lines" in d:
        size = k.fit(d["lines"], 100, 900)
        lines = d["lines"]
    else:
        size = k.wrap_fit(d["text"], 92, 900, 4)
        lines = k.lines(d["text"], size, 900)
    step = size * 1.12
    bottom = obj_y - (150 if obj != "none" else -150)
    top = bottom - step * len(lines)
    for i, line in enumerate(lines):
        n = ctx.node(k.text(line, size), 540, top + i * step + step / 2, z=5)
        n.show(s + 0.3 + i * 0.25, 0.75, rise=True)

    if obj == "vinyl":
        ctx.center.pose(s + 0.15, 0.8, "vinyl", cx=540, cy=obj_y, s=0.42, show={"scale_from": 0.85})
        ctx.center.vinyl.spin = (s + d.get("spin_at", 1.9), 150.0, 1.0)
    elif obj == "helmets":
        helmets = ctx.node(objects.helmets(380, 200, th.foreground, th.accent), 540, obj_y, z=3)
        helmets.show(s + 0.2, 0.9, dy=0, scale_from=0.92)

    y = obj_y + 190
    if d.get("body"):
        body = ctx.node(k.wrap(d["body"], 40, 860, th.muted, "serif_italic"), 540, 0, z=5)
        body.set(0, y=y + body.sprite.height / 2)
        body.show(s + d.get("body_at", 1.0), 0.7, dy=16)
        y += body.sprite.height + 30
    if d.get("question"):
        q_size = k.fit([d["question"]], 60, 900, "display_italic")
        q = ctx.node(k.text(d["question"], q_size, th.accent, "display_italic"), 540, y + 70, z=5)
        q.show(s + 1.55, 0.7, rise=True)


@section("object")
def object_(ctx: MapContext, sec: Section) -> None:
    """The central object arrives: sleeve + record, artist above, huge title, lines below.

    data: above?, below? (small caps), feat? (italic), rays?: bool
    """
    k, d, s, e = ctx.kit, sec.data, sec.start, sec.end
    th = k.t
    c = ctx.center
    c.place(c.vinyl, s - 0.25, 0.85, True, x=640, y=900, scale=0.92)
    if not c.vinyl.spin:
        c.vinyl.spin = (s + 0.4, 150.0, 1.0)
    c.place(c.sleeve, s, 0.6, True, x=500, y=900, scale=1.0,
            show={"dy": 150, "scale_from": None, "easing": "ease_out_expo"})
    c.place(c.title, s + 0.6, 0.85, True, x=540, y=1190, scale=1.0, show={"rise": True, "scale_from": None})
    c.hub.set(max(s, c.hub.keys[-1].t), x=566, y=900)

    if d.get("above"):
        n = ctx.node(k.label(d["above"], 30, th.foreground, 8), 540, 640, z=5)
        n.show(s + 0.45, 0.6)
    y = 1300
    if d.get("feat"):
        size = k.fit([d["feat"]], 40, 920, "display_italic")
        n = ctx.node(k.text(d["feat"], size, th.accent, "display_italic"), 540, y, z=5)
        n.show(s + 1.1, 0.7, rise=True)
        y += 70
    if d.get("below"):
        n = ctx.node(k.label(d["below"], 24, th.muted), 540, y, z=5)
        n.show(s + 1.15, 0.6)
    if d.get("rays"):
        # First thin lines start to radiate from the object.
        for i, deg in enumerate((200, 160, 20, -20, -60, -120)):
            a = math.radians(deg)
            end = ctx.anchor(566 + 440 * math.cos(a), 900 - 440 * math.sin(a))
            ctx.link(c.hub, end, th.line, e - 1.5 + i * 0.1, dur=0.7, gap_a=300, width=1, dash=6)
