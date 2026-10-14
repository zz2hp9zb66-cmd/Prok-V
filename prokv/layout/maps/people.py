"""branches · musicians · core"""

from __future__ import annotations

from prokv.content.track_map import Section
from prokv.graphics import objects, shapes
from prokv.layout.maps.base import MapContext, section

SLOTS = {
    6: [(280, 640), (800, 640), (800, 1230), (540, 1460), (280, 1230), (540, 410)],
    5: [(280, 640), (800, 640), (800, 1230), (540, 1460), (280, 1230)],
    4: [(280, 640), (800, 640), (800, 1230), (280, 1230)],
    3: [(280, 700), (800, 700), (540, 1400)],
    2: [(280, 900), (800, 900)],
}


def _bottom_line(ctx: MapContext, text: str, t: float, style: str = "italic") -> None:
    k = ctx.kit
    if style == "tag":
        size = k.fit([text], 56, 920)
        sprite = k.text(text, size, k.t.foreground)
    else:
        size = k.wrap_fit(text, 58, 920, 2, "display_italic")
        sprite = k.wrap(text, size, 920, k.t.accent, "display_italic")
    ctx.node(sprite, 540, 1500, z=5).show(t, 0.7, rise=True)


@section("branches")
def branches(ctx: MapContext, sec: Section) -> None:
    """1–3 main names branch out from the object (a triangle when there are three).

    data: items: [{name, role}], tag? (e.g. "ELECTRONIC × POP × DISCO"), outro? (italic line)
    """
    k, d, s, e = ctx.kit, sec.data, sec.start, sec.end
    th = k.t
    c = ctx.center
    cx, cy = 540, 930
    c.pose(s, 0.8, "object", cx=cx, cy=cy, s=0.45, title_scale=0.32, title_y=cy + 0.45 * 200 + 40)
    items = d["items"]
    positions = {1: [(540, 500)], 2: [(300, 1330), (780, 1330)], 3: [(540, 500), (300, 1330), (780, 1330)]}
    step = min(0.8, (sec.length - 2.8) / len(items))
    anchors = []
    for i, (item, pos) in enumerate(zip(items, positions[len(items)])):
        t0 = s + 0.7 + i * step
        size = k.fit([item["name"]], 44, 440)
        sprite = k.stack([k.text(item["name"], size), k.text(item["role"], 30, th.muted, "serif_italic")],
                         "center", 4)
        node = ctx.node(sprite, *pos, z=4)
        anchor = ctx.anchor(*pos)
        anchors.append(anchor)
        ctx.link(c.hub, anchor, th.line, t0, dur=0.5, gap_a=150 if pos[1] < cy else 215,
                 gap_b=sprite.height / 2 + 26)
        node.show(t0 + 0.35, 0.6, dy=14)
    if len(anchors) == 3:
        t_tri = s + 0.7 + 3 * step + 0.2
        for i in range(3):
            ctx.link(anchors[i], anchors[(i + 1) % 3], th.line, t_tri + i * 0.15, dur=0.5, gap_a=150,
                     gap_b=150, width=1, dash=6, opacity=0.8)
    if d.get("tag"):
        _bottom_line(ctx, d["tag"], e - 1.4, "tag")
    elif d.get("outro"):
        _bottom_line(ctx, d["outro"], e - 1.35)


@section("musicians")
def musicians(ctx: MapContext, sec: Section) -> None:
    """Musicians appear around the title, one line per beat step (1.5 beats).

    data: items: [{instrument, name, texture}], caption?, keep?
    textures: drums, bass, guitar, rhodes, synth, lyricon, vocals, production
    """
    k, d, s, e = ctx.kit, sec.data, sec.start, sec.end
    th = k.t
    c = ctx.center
    hub = (540, 880)
    c.pose(s - 0.1, 0.8, "title", cx=hub[0], cy=hub[1], vinyl_y=800, title_y=930)
    items = d["items"]
    slots = SLOTS[len(items)]
    caption_room = 1.7 if d.get("caption") else 0.6
    step = 1.5 * ctx.beat
    if s + 0.4 + step * (len(items) - 1) + 0.9 > e - caption_room:
        step = ctx.beat
    for i, (m, (x, y)) in enumerate(zip(items, slots)):
        t0 = s + 0.4 + i * step
        icon = ctx.node(objects.instrument(m["texture"], 92, th.foreground, th.accent), x, y - 72, z=4)
        name_size = k.fit([m["name"]], 36, 360)
        sprite = k.stack([k.label(m["instrument"], 22), k.text(m["name"], name_size)], "center", 4)
        text = ctx.node(sprite, x, y + 6 + sprite.height / 2, z=4)
        anchor = ctx.anchor(x, y)
        straight_up = y < hub[1] - 200 and abs(x - hub[0]) < 50
        link = ctx.link(c.hub, anchor, th.line, t0, dur=0.6 * ctx.beat, gap_a=175 if straight_up else 130,
                        gap_b=115, easing="ease_out")
        icon.show(t0 + 0.6 * ctx.beat, 0.5, dy=0, scale_from=0.9)
        text.show(t0 + 0.8 * ctx.beat, 0.5, dy=12)
        ctx.named[f"musician:{m['instrument']}"] = (text, icon, link)
    if d.get("caption"):
        cap = k.wrap(d["caption"], 36, 900, th.muted, "serif_italic")
        ctx.node(cap, 540, 1580, z=5).show(e - 1.6, 0.6, dy=12)


@section("core")
def core(ctx: MapContext, sec: Section) -> None:
    """The turn: only two musicians stay; big drawings of their instruments, a beat pulse.

    Follows a musicians section with "keep": true.
    data: pair: [instrument, instrument], text: [lines], pair_label?
    """
    k, d, s, e = ctx.kit, sec.data, sec.start, sec.end
    th = k.t
    carried = ctx.take_carried()
    keep = []
    for name in d["pair"]:
        text, icon, link = ctx.named[f"musician:{name}"]
        keep.append(text)
    ctx.fade([x for x in carried if x not in keep], s - 0.1, 0.45)
    ctx.center.pose(s - 0.1, 0.45, "hidden")
    left, right = keep
    left.animate(s + 0.1, 0.9, "ease_in_out", x=290, y=1150)
    right.animate(s + 0.1, 0.9, "ease_in_out", x=800, y=1150)
    size = k.fit(d["text"], 80, 920)
    for i, line in enumerate(d["text"]):
        ctx.node(k.text(line, size), 540, 440 + i * size * 1.12, z=5).show(s + 0.35 + i * 0.3, 0.75, rise=True)
    textures = {name: next(m for m in _musicians_of(ctx, name)) for name in d["pair"]}
    drawings = []
    for i, (name, x) in enumerate(zip(d["pair"], (290, 800))):
        tex = textures[name]
        if tex == "drums":
            sprite = objects.drum_kit(380, 300, th.foreground, th.accent)
        elif tex == "bass":
            sprite = objects.bass_guitar(170, 400, th.foreground, th.accent)
        else:
            sprite = objects.instrument(tex, 300, th.foreground, th.accent)
        node = ctx.node(sprite, x, 880 if tex != "bass" else 850, z=3)
        node.show(s + 1.0 + i * 0.4, 0.7, dy=24)
        drawings.append(node)
    label = d.get("pair_label") or " × ".join(d["pair"])
    ctx.node(k.text(label, k.fit([label], 54, 920)), 540, 1310, z=5).show(s + 1.9, 0.6, dy=14)
    t_pulse = s + 2.3
    for i in range(4):
        x = 330 + i * 140
        dot = ctx.node(k.dot(22), x, 1420, z=5)
        dot.show(t_pulse + i * 0.08, 0.3, dy=0, scale_from=0.3)
        dot.pulse = (t_pulse + 0.4 + i * ctx.beat, e - 0.1, 4 * ctx.beat, 0.7)
        if i < 3:
            ctx.node(shapes.rule(70, 2, th.line), x + 70, 1420, z=4).show(t_pulse + i * 0.08 + 0.1, 0.3, dy=0)


def _musicians_of(ctx: MapContext, instrument: str):
    for sec in ctx.ep.sections:
        if sec.type == "musicians":
            for m in sec.data["items"]:
                if m["instrument"] == instrument:
                    yield m["texture"]
