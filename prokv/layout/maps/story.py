"""statement · chain · cycle · afterlife · awards"""

from __future__ import annotations

import math

from prokv.content.track_map import Section
from prokv.layout.maps.base import MapContext, edge_gap, is_year, section


@section("statement")
def statement(ctx: MapContext, sec: Section) -> None:
    """The map freezes and dims; one huge word, a pause, then the answer.

    data: words: ["SAMPLE?", "NO."], caption?, emphasis?, dim_map?: bool
    """
    k, d, s, e = ctx.kit, sec.data, sec.start, sec.end
    th = k.t
    if d.get("dim_map", True):
        carried = ctx.take_carried()
        for item in carried:
            if hasattr(item, "keys"):
                item.animate(max(s, item.keys[-1].t), 0.5, "ease_in_out", opacity=0.1)
        ctx.fade([x for x in carried if not hasattr(x, "keys")], s, 0.5)
        ctx.center.dim(s, 0.1)
    words = d["words"]
    first_size = k.fit([words[0]], 230, 920)
    first = ctx.node(k.text(words[0], first_size), 540, 820, z=6)
    first.show(s + 0.35, 0.8, rise=True)
    if len(words) > 1:
        t2 = s + d.get("pause", 1.25) + 0.35
        first.animate(t2, 0.6, "ease_in_out", y=600, scale=0.45, opacity=0.35)
        second = ctx.node(k.text(words[1], k.fit([words[1]], 260, 920), th.accent), 540, 860, z=6)
        second.show(t2 + 0.15, 0.7, rise=True)
    y = 1110
    t_cap = s + d.get("caption_at", 2.35)
    if d.get("caption"):
        cap = k.wrap(d["caption"], 38, 900, th.muted, "serif_italic")
        ctx.node(cap, 540, y + cap.height / 2, z=6).show(t_cap, 0.6, dy=12)
        y += cap.height + 24
    if d.get("emphasis"):
        size = k.wrap_fit(d["emphasis"], 50, 920, 3)
        emph = k.wrap(d["emphasis"], size, 920)
        ctx.node(emph, 540, y + emph.height / 2, z=6).show(t_cap + 0.35, 0.7, rise=True)


@section("chain")
def chain(ctx: MapContext, sec: Section) -> None:
    """A line runs back in time from one name, through a vertical chain of steps.

    data: origin?, items: [..] (years render in small caps), caption?
    """
    k, d, s, e = ctx.kit, sec.data, sec.start, sec.end
    th = k.t
    ctx.center.pose(s - 0.1, 0.45, "hidden")
    items = d["items"]
    top, bottom = (440 if d.get("origin") else 360), 1330
    gap = (bottom - top) / max(len(items) - 1, 1)
    caption_room = 2.0 if d.get("caption") else 0.6
    step = min(0.42, (sec.length - caption_room - 0.9) / len(items))
    prev = None
    if d.get("origin"):
        origin = ctx.node(k.stack([k.label("FROM", 20, th.muted), k.text(d["origin"], 46)]), 540, 300, z=5)
        origin.show(s + 0.15, 0.6, dy=12)
        prev = origin
    for i, item in enumerate(items):
        t0 = s + 0.5 + i * step
        last = i == len(items) - 1
        if is_year(item):
            sprite = k.label(item, 34, th.accent, 6)
        else:
            size = k.fit([item], 64 if last else 52, 900)
            sprite = k.text(item, size, th.accent if last else th.foreground)
        node = ctx.node(sprite, 540, top + i * gap, z=5)
        node.show(t0, 0.5, dy=0 if not last else 10, scale_from=0.94)
        if prev is not None:
            ctx.link(prev, node, th.line, t0 - 0.22, dur=0.3, gap_a=prev.sprite.height / 2 + 10,
                     gap_b=sprite.height / 2 + 10, arrow=True, width=2, easing="ease_out")
        prev = node
    if d.get("caption"):
        cap = k.wrap(d["caption"], 36, 920, th.muted, "serif_italic")
        ctx.node(cap, 540, 1470 + cap.height / 2, z=5).show(e - caption_room, 0.6, dy=12)


@section("cycle")
def cycle(ctx: MapContext, sec: Section) -> None:
    """Steps around a circle with arrows; the last arrow closes the loop.

    data: items: [..], caption?
    """
    k, d, s, e = ctx.kit, sec.data, sec.start, sec.end
    th = k.t
    cx, cy, rx, ry = 540, 860, 330, 420
    ctx.center.pose(s, 0.6, "vinyl", cx=cx, cy=cy, s=0.32)
    items = d["items"]
    n = len(items)
    step = min(0.42, (sec.length - 1.8) / (n + 1))
    nodes = []
    for i, item in enumerate(items):
        a = -math.pi / 2 + i * 2 * math.pi / n
        last = i == n - 1
        size = k.fit([item], 46, 300)
        sprite = k.text(item, size, th.accent if last else th.foreground)
        node = ctx.node(sprite, cx + rx * math.cos(a), cy + ry * math.sin(a), z=5)
        t0 = s + 0.3 + i * step
        node.show(t0, 0.5, dy=0, scale_from=0.92)
        if nodes:
            _arc_link(ctx, nodes[-1], node, th.line, t0 - 0.25, 0.35, 2)
        nodes.append(node)
    _arc_link(ctx, nodes[-1], nodes[0], th.accent, s + 0.3 + n * step, 0.6, 3)
    if d.get("caption"):
        cap = k.wrap(d["caption"], 38, 900, th.muted, "serif_italic")
        ctx.node(cap, 540, 1400 + cap.height / 2, z=5).show(e - 1.5, 0.6, dy=12)


@section("afterlife")
def afterlife(ctx: MapContext, sec: Section) -> None:
    """Arrows point outwards: later records that sampled / reused the track.

    data: question, caption, items: [{artist, year}]
    """
    k, d, s, e = ctx.kit, sec.data, sec.start, sec.end
    th = k.t
    c = ctx.center
    c.pose(s + 0.1, 0.6, "title", cx=540, cy=880, vinyl_y=760, title_y=880, title_scale=0.55)
    hub = ctx.anchor(540, 900)
    size = k.fit([d["question"]], 66, 900, "display_italic")
    ctx.node(k.text(d["question"], size, th.foreground, "display_italic"), 540, 420, z=5).show(s + 0.3, 0.7,
                                                                                               rise=True)
    if d.get("caption"):
        ctx.node(k.label(d["caption"], 20, th.accent, 4), 540, 510, z=5).show(s + 0.7, 0.5)
    positions = {1: [(540, 1350)], 2: [(300, 1300), (780, 1300)], 3: [(260, 1240), (540, 1400), (820, 1240)]}
    for i, (item, pos) in enumerate(zip(d["items"], positions[len(d["items"])])):
        t0 = s + 1.05 + i * 1.5 * ctx.beat
        size = k.fit([item["artist"]], 40, 470)
        sprite = k.stack([k.text(item["artist"], size), k.label(item["year"], 26)], "center", 6)
        node = ctx.node(sprite, *pos, z=4)
        anchor = ctx.anchor(*pos)
        ctx.link(hub, anchor, th.accent, t0, dur=0.55, gap_a=60, gap_b=sprite.height / 2 + 30, arrow=True)
        node.show(t0 + 0.4, 0.6, dy=14)


@section("awards")
def awards(ctx: MapContext, sec: Section) -> None:
    """A year in the centre, lines to the awards it brought.

    data: year, label? (e.g. "GRAMMY"), items: [..], caption?
    """
    k, d, s, e = ctx.kit, sec.data, sec.start, sec.end
    th = k.t
    ctx.center.pose(s - 0.1, 0.45, "hidden")
    if d.get("label"):
        ctx.node(k.label(d["label"], 28, th.accent, 10), 540, 520, z=5).show(s + 0.3, 0.5)
    year = ctx.node(k.text(d["year"], 230), 540, 700, z=5)
    year.show(s + 0.15, 0.8, rise=True)
    hub = ctx.anchor(540, 760)
    items = d["items"]
    positions = {1: [(540, 1120)], 2: [(290, 1120), (790, 1120)], 3: [(220, 1120), (540, 1200), (860, 1120)]}
    for i, (item, pos) in enumerate(zip(items, positions[len(items)])):
        t0 = s + 0.9 + i * 0.45
        sprite = k.wrap(item, k.wrap_fit(item, 42, 400, 3), 400)
        node = ctx.node(sprite, *pos, z=5)
        anchor = ctx.anchor(*pos)
        ctx.link(hub, anchor, th.accent, t0, dur=0.5, gap_a=130, gap_b=sprite.height / 2 + 26, arrow=True)
        node.show(t0 + 0.35, 0.6, dy=12)
    if d.get("caption"):
        cap = k.wrap(d["caption"], 36, 900, th.muted, "serif_italic")
        ctx.node(cap, 540, 1400 + cap.height / 2, z=5).show(s + 2.1, 0.6, dy=12)


def _arc_link(ctx: MapContext, a, b, color: str, t: float, dur: float, width: int) -> None:
    va, vb = a.value(1e9), b.value(1e9)
    dx, dy = vb["x"] - va["x"], vb["y"] - va["y"]
    ctx.link(a, b, color, t, dur=dur, gap_a=edge_gap(a.sprite, dx, dy), gap_b=edge_gap(b.sprite, dx, dy),
             arrow=True, width=width, easing="ease_out")
