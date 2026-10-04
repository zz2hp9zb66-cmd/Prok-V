"""final_map · outro"""

from __future__ import annotations

import math

from PIL import Image

from prokv.content.track_map import Section
from prokv.layout.maps.base import MapContext, edge_gap, section


@section("final_map")
def final_map(ctx: MapContext, sec: Section) -> None:
    """The camera pulls back: the whole map around the title at once.

    Rings mode — data: inner: [..], outer: [..] (outer ring in thinner dashed lines).
    Arrows mode — data: top?: "DAFT PUNK", subtitle?: "2013",
                  nodes: [{text, dir: "in" | "out"}] ("in" = flows into the track).
    """
    k, d, s, e = ctx.kit, sec.data, sec.start, sec.end
    th = k.t
    cam = ctx.stage.camera
    rings = "inner" in d
    zoom = 0.62 if rings else 0.74
    cam.set(max(s - 0.1, cam.keys[-1].t), cx=540, cy=880)
    cam.animate(s, 1.4, "ease_in_out", zoom=zoom)
    cam.animate(s + 1.4, max(sec.length - 1.5, 0.1), "linear", zoom=zoom - 0.04)
    c = ctx.center
    title_scale = 0.85 if rings else 0.6
    c.pose(s, 1.4, "title", cx=540, cy=880, vinyl_y=760 if not rings else 740, vinyl_scale=0.45 if rings else 0.35,
           title_y=900, title_scale=title_scale)
    hub = ctx.anchor(540, 880)

    if rings:
        for i, name in enumerate(d["inner"]):
            a = -math.pi / 2 + i * 2 * math.pi / len(d["inner"])
            node = ctx.node(k.label(name, 30, th.foreground, 3), 540 + 390 * math.cos(a), 880 + 600 * math.sin(a))
            t0 = s + 0.4 + i * 0.12
            ctx.link(hub, node, th.line, t0, dur=0.45, gap_a=170, gap_b=30, width=2)
            node.show(t0 + 0.3, 0.45, dy=0, scale_from=0.9)
        n_out = len(d.get("outer", []))
        for i, name in enumerate(d.get("outer", [])):
            a = -math.pi / 2 + math.pi / n_out + i * 2 * math.pi / n_out
            node = ctx.node(k.text(name, 48, th.accent, "display_italic"), 540 + 700 * math.cos(a),
                            880 + 1000 * math.sin(a))
            t0 = s + 1.9 + i * 0.14
            ctx.link(hub, node, th.line, t0, dur=0.55, gap_a=170, gap_b=50, width=1, dash=5, opacity=0.7)
            node.show(t0 + 0.35, 0.5, dy=0, scale_from=0.9)
        return

    if d.get("subtitle"):
        ctx.node(k.label(d["subtitle"], 34, th.accent, 8), 540, 975).show(s + 0.5, 0.5)
    if d.get("top"):
        top = ctx.node(k.text(d["top"], 64), 540, 880 - 760)
        top.show(s + 0.95, 0.5, dy=0, scale_from=0.9)  # once the camera has pulled back
        ctx.link(top, hub, th.accent, s + 1.1, dur=0.45, gap_a=50, gap_b=200, arrow=True, width=3)
    nodes = d["nodes"]
    # Keep arrows clear of the title + record group in the centre.
    center_box = Image.new("L", (int(c.title.sprite.width * title_scale), 260))
    # Spread around an ellipse, leaving the top for the artist.
    span = 2 * math.pi * 0.76
    for i, item in enumerate(nodes):
        a = -math.pi / 2 + (2 * math.pi - span) / 2 + span * i / max(len(nodes) - 1, 1)
        x, y = 540 + 500 * math.cos(a), 900 + 660 * math.sin(a)
        incoming = item.get("dir") == "in"
        sprite = k.text(item["text"], k.fit([item["text"]], 44, 380),
                        th.muted if incoming else th.foreground, "display_italic" if incoming else "display")
        node = ctx.node(sprite, x, y)
        t0 = s + 0.7 + i * min(0.16, (sec.length - 1.6) / len(nodes))
        gap_node = edge_gap(sprite, math.cos(a), math.sin(a))
        gap_hub = edge_gap(center_box, math.cos(a), math.sin(a), pad=24)
        if incoming:
            ctx.link(node, hub, th.line, t0, dur=0.45, gap_a=gap_node, gap_b=gap_hub, arrow=True, width=2)
        else:
            ctx.link(hub, node, th.line, t0, dur=0.45, gap_a=gap_hub, gap_b=gap_node, arrow=True, width=2)
        node.show(t0 + 0.3, 0.45, dy=0, scale_from=0.9)


@section("outro")
def outro(ctx: MapContext, sec: Section) -> None:
    """Everything clears; the record, closing lines and the series card.

    data: lines: [..], card?: text (default "№001 — TRACK" under the series name), cta?, vinyl?: bool
    """
    k, d, s, e = ctx.kit, sec.data, sec.start, sec.end
    th = k.t
    cam = ctx.stage.camera
    cam.animate(max(s, cam.keys[-1].t), 0.9, "ease_in_out", cx=540, cy=900, zoom=1.0)
    if d.get("vinyl", True):
        ctx.center.pose(s, 0.9, "vinyl", cx=540, cy=760, s=0.42)
    else:
        ctx.center.pose(s, 0.45, "hidden")
    lines = d["lines"]
    size = k.fit(lines, 86, 920)
    line_nodes = [ctx.node(k.text(line, size), 540, 1010 + i * size * 1.15, z=5, fixed=True)
                  for i, line in enumerate(lines)]
    for i, n in enumerate(line_nodes):
        n.show(s + 0.45 + i * 0.3, 0.7, rise=True)
    roomy = sec.length >= 2.8
    if roomy:
        for n in line_nodes:
            n.hide(s + 1.65, 0.35, dy=0)
        y, t_card = 990, s + 1.95
    else:
        y, t_card = 1010 + len(lines) * size * 1.15 + 40, s + 1.0
    if d.get("card"):
        card_size = k.fit([d["card"]], 56 if not roomy else 76, 920)
        ctx.node(k.text(d["card"], card_size, th.accent), 540, y + 30, z=5, fixed=True).show(t_card, 0.6, rise=True)
        y += 30 + card_size
    else:
        ctx.node(k.label(ctx.ep.series, 28, th.accent, 8), 540, y, z=5, fixed=True).show(t_card, 0.5)
        ep_text = f"№{ctx.ep.number:03d} — {ctx.ep.track.upper()}"
        ctx.node(k.text(ep_text, k.fit([ep_text], 76, 920)), 540, y + 85, z=5, fixed=True).show(t_card + 0.1, 0.6,
                                                                                             rise=True)
        y += 85 + 60
    if d.get("cta"):
        ctx.node(k.text(d["cta"], 38, th.muted, "serif_italic"), 540, y + 35, z=5, fixed=True).show(
            t_card + 0.4, 0.5)
