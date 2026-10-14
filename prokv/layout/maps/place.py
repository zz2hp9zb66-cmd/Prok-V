"""coordinates · places"""

from __future__ import annotations

from prokv.content.track_map import Section
from prokv.graphics import objects
from prokv.layout.maps.base import MapContext, left_x, right_x, section

ENDS = {"left": (110, 900), "right": (970, 900), "top": (566, 410), "bottom": (566, 1470)}
GAPS = {"left": 170, "right": 170, "top": 130, "bottom": 200}
DEFAULT_SIDES = {"ARTIST": "left", "ALBUM": "right", "YEAR": "top", "LABEL": "bottom"}


@section("coordinates")
def coordinates(ctx: MapContext, sec: Section) -> None:
    """Up to four lines draw out from the object, one by one, each ending in a fact.

    data: items: [{label, value, side?: left|right|top|bottom}], keep?
    """
    k, s = ctx.kit, sec.start
    th = k.t
    c = ctx.center
    c.pose(s, 0.75, "object", cx=566, cy=900, s=0.55, title_scale=0.4, title_y=1060)
    items = sec.data["items"]
    free = [side for side in ("left", "right", "top", "bottom")]
    step = min(0.7, (sec.length - 1.9) / max(len(items) - 1, 1))
    for i, item in enumerate(items):
        side = item.get("side") or DEFAULT_SIDES.get(item["label"].upper())
        side = side if side in free else free[0]
        free.remove(side)
        t0 = s + 0.5 + i * step
        ex, ey = ENDS[side]
        end = ctx.node(k.dot(14), ex, ey, z=3)
        ctx.link(c.hub, end, th.line, t0, dur=0.6, gap_a=GAPS[side], width=2)
        end.show(t0 + 0.5, 0.3, dy=0, scale_from=0.3)
        horizontal = side in ("left", "right")
        sprite = k.info(item["label"], item["value"], {"left": "left", "right": "right"}.get(side, "center"),
                        40 if horizontal else 46, max_w=300 if horizontal else 860)
        if side == "left":
            pos = (left_x(sprite, 96), ey - sprite.height / 2 - 26)
        elif side == "right":
            pos = (right_x(sprite, 984), ey - sprite.height / 2 - 26)
        elif side == "top":
            pos = (ex, ey - sprite.height / 2 - 28)
        else:
            pos = (ex, ey + sprite.height / 2 + 28)
        info = ctx.node(sprite, *pos, z=4)
        info.show(t0 + 0.45, 0.6, dy=-16 if side == "top" else 16)


@section("places")
def places(ctx: MapContext, sec: Section) -> None:
    """The camera eases down to where the record was made.

    One place: city-grid fragment, "CITY → STUDIO", caption, an arrow back to the object.
    Two places: two pins with a line between the cities and a caption.
    data: places: [{city, place?, caption?}], caption?, keep?
    """
    k, d, s, e = ctx.kit, sec.data, sec.start, sec.end
    th = k.t
    ctx.take_carried()  # whatever map is on screen moves with the camera
    cam = ctx.stage.camera
    cam.animate(s, 0.9, "ease_in_out", cy=1230, zoom=0.7)
    cam.animate(e - 0.7, 0.8, "ease_in_out", cy=900, zoom=1.0)
    places = d["places"]

    if len(places) == 1:
        p = places[0]
        frag_c = (790, 1800)
        frag = ctx.node(objects.city_fragment(340, 230, k.p), *frag_c, z=2)
        frag.show(s + 0.7, 0.7, dy=24, scale_from=0.96)
        pin = ctx.anchor(frag_c[0] - 170 + 0.62 * 340, frag_c[1] - 115 + 0.45 * 230)
        city = k.label(p["city"], 28, th.accent, 6)
        ctx.node(city, left_x(city, 110), 1712, z=4).show(s + 1.1, 0.6)
        y = 1712 + 26
        if p.get("place"):
            words = ("→ " + p["place"]).split()
            half = max(2, (len(words) + 1) // 2)
            studio = k.stack([k.text(" ".join(words[:half]), 44), k.text(" ".join(words[half:]), 44)]
                             if len(words) > 3 else [k.text(" ".join(words), 44)], "left", 2)
            ctx.node(studio, left_x(studio, 110), y + studio.height / 2, z=4).show(s + 1.5, 0.7, rise=True)
            y += studio.height + 34
        caption = p.get("caption") or d.get("caption")
        if caption:
            cap = k.label(caption, 22, th.muted)
            ctx.node(cap, left_x(cap, 110), y, z=4).show(s + 2.0, 0.5)
        ctx.link(pin, ctx.center.hub, th.accent, s + 2.4, dur=0.9, gap_a=26, gap_b=200, width=2, arrow=True)
        return

    # Two cities, joined by a line.
    pins = []
    for i, (p, x) in enumerate(zip(places, (300, 780))):
        frag = ctx.node(objects.city_fragment(280, 180, k.p, angle=8 if i else -6), x, 1760, z=2)
        frag.show(s + 0.7 + i * 0.4, 0.7, dy=24, scale_from=0.96)
        pins.append(ctx.anchor(x - 140 + 0.62 * 280, 1760 - 90 + 0.45 * 180))
        city = k.label(p["city"], 30, th.accent, 6)
        ctx.node(city, x, 1885, z=4).show(s + 1.0 + i * 0.4, 0.6)
        if p.get("place"):
            place = k.wrap(p["place"], 40, 380)
            ctx.node(place, x, 1915 + place.height / 2, z=4).show(s + 1.2 + i * 0.4, 0.6, rise=True)
    ctx.link(pins[0], pins[1], th.accent, s + 1.9, dur=0.8, gap_a=12, gap_b=12, width=3)
    if d.get("caption"):
        cap = k.wrap(d["caption"], 38, 900, th.muted, "serif_italic")
        ctx.node(cap, 540, 1540, z=5, fixed=True).show(s + 2.4, 0.6, dy=12)
