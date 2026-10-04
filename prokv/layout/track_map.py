"""Choreography of the "Карта одного трека" (one-track map) format, 40 seconds.

0–3 hook · 3–6 object · 6–10 coordinates · 10–14 place · 14–19 people ·
19–25 musicians (on the beat) · 25–29 the turn · 29–33 afterlife ·
33–37 influence (zoom out) · 37–40 final.

World coordinates equal screen pixels at zoom 1; the camera centre maps to
FOCUS. Everything is driven by a TrackMap (facts + texts) and the VisualStyle.
"""

from __future__ import annotations

import math

from PIL import Image

from prokv.animation.stage import Camera, Node, Stage
from prokv.config import VideoSpec
from prokv.content.track_map import TrackMap
from prokv.graphics import objects, shapes
from prokv.style import DEFAULT_STYLE, VisualStyle
from prokv.typography import FontBook, label_sprite, text_sprite

DURATION = 40.0
FOCUS = (540, 900)


class _Kit:
    """Sprite factory bound to the style."""

    def __init__(self, style: VisualStyle) -> None:
        self.style = style
        self.fonts = FontBook(style.fonts)
        self.p = style.palette
        self.t = style.themes["cream"]

    def text(self, text: str, size: int, color: str | None = None, role: str = "display") -> Image.Image:
        return text_sprite(text, self.fonts.get(role, size), color or self.t.foreground)

    def label(self, text: str, size: int = 24, color: str | None = None, tracking: int = 5) -> Image.Image:
        return label_sprite(text, self.fonts.get("mono", size), color or self.t.accent, tracking)

    def fit(self, lines: list[str], max_size: int, max_w: int, role: str = "display") -> int:
        size = max_size
        while size > 20 and max(self.fonts.get(role, size).getlength(l) for l in lines) > max_w:
            size -= 2
        return size

    @staticmethod
    def stack(sprites: list[Image.Image], align: str = "center", gap: int = 6) -> Image.Image:
        w = max(s.width for s in sprites)
        h = sum(s.height for s in sprites) + gap * (len(sprites) - 1)
        out = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        y = 0
        for s in sprites:
            x = {"left": 0, "right": w - s.width}.get(align, (w - s.width) // 2)
            out.alpha_composite(s, (x, y))
            y += s.height + gap
        return out

    def info(self, label: str, value: str, align: str = "center", value_size: int = 46,
             value_role: str = "display", value_color: str | None = None) -> Image.Image:
        return self.stack([self.label(label), self.text(value, value_size, value_color, value_role)], align)

    def dot(self, d: int = 14, color: str | None = None) -> Image.Image:
        return shapes.dot(d, color or self.t.accent)


def _left(sprite: Image.Image, x: float) -> float:
    return x + sprite.width / 2


def _right(sprite: Image.Image, x: float) -> float:
    return x - sprite.width / 2


def build_track_map(tm: TrackMap, style: VisualStyle = DEFAULT_STYLE, spec: VideoSpec = VideoSpec()):
    """Return (Stage, overlay) for StageRenderer."""
    k = _Kit(style)
    p, th = k.p, k.t
    beat = 60.0 / tm.bpm
    stage = Stage(spec.width, spec.height, DURATION, FOCUS, Camera(*FOCUS), th.background)
    W = spec.width
    line_c = th.line

    # ---- 0:00–0:03 HOOK -------------------------------------------------------
    vinyl = stage.node(objects.vinyl_record(420, p), 540, 900, z=1, scale=0.42)
    vinyl.show(0.15, 0.8, dy=0, scale_from=0.85)
    hook_size = k.fit(tm.hook, 100, 900)
    hook = [stage.node(k.text(line, hook_size), 540, 540 + i * hook_size * 1.12, z=5) for i, line in enumerate(tm.hook)]
    for i, n in enumerate(hook):
        n.show(0.3 + i * 0.3, 0.75, rise=True)
    q_size = k.fit([tm.hook_question], 60, 900, "display_italic")
    question = stage.node(k.text(tm.hook_question, q_size, th.accent, "display_italic"), 540, 1190, z=5)
    question.show(1.55, 0.7, rise=True)
    vinyl.spin = (1.9, 150.0, 1.0)
    for n in hook + [question]:
        n.hide(2.55, 0.4)

    # ---- 0:03–0:06 OBJECT -----------------------------------------------------
    cover = Image.open(tm.cover_image) if tm.cover_image else None
    sleeve = stage.node(objects.sleeve(400, p, tm.album, tm.artist, f"{tm.label} · {tm.year}", k.fonts, cover),
                        500, 900, z=2)
    vinyl.animate(2.75, 0.85, "ease_in_out", x=640, scale=0.92)
    sleeve.show(3.0, 0.6, dy=150, easing="ease_out_expo")
    artist_top = stage.node(k.label(tm.artist, 30, th.foreground, 8), 540, 640, z=5)
    artist_top.show(3.45, 0.6)
    title_size = k.fit([tm.track.upper()], 150, 920)
    title = stage.node(k.text(tm.track.upper(), title_size), 540, 1190, z=5)
    title.show(3.6, 0.85, rise=True)
    subtitle = stage.node(k.label(f"{tm.subtitle} / {tm.year}", 24, th.muted), 540, 1300, z=5)
    subtitle.show(4.15, 0.6)

    def pose(t: float, dur: float, cx: float, cy: float, s: float, title_scale: float, title_y: float,
             easing: str = "ease_in_out") -> None:
        sleeve.animate(t, dur, easing, x=cx - 66 * s, y=cy, scale=s)
        vinyl.animate(t, dur, easing, x=cx + 74 * s, y=cy, scale=0.92 * s)
        title.animate(t, dur, easing, x=cx, y=title_y, scale=title_scale)

    # ---- 0:06–0:10 BASE COORDINATES ------------------------------------------
    artist_top.hide(5.85, 0.4)
    subtitle.hide(5.85, 0.4)
    center = (566, 900)
    pose(6.0, 0.75, *center, 0.55, 0.4, 1060)
    hub = stage.node(k.dot(2), *center)  # invisible anchor for links
    ends = {
        "left": (110, 900), "right": (W - 110, 900), "top": (566, 410), "bottom": (566, 1470),
    }
    gaps = {"left": 170, "right": 170, "top": 130, "bottom": 200}
    coord_info = {
        "left": ("ARTIST", tm.artist), "right": ("ALBUM", tm.album),
        "top": ("YEAR", tm.year), "bottom": ("LABEL", tm.label),
    }
    coord_nodes: list[Node] = []
    coord_links = []
    for i, side in enumerate(("left", "right", "top", "bottom")):
        t0 = 6.5 + i * 0.7
        end = stage.node(k.dot(14), *ends[side], z=3)
        coord_links.append(stage.link(hub, end, line_c, t0, dur=0.6, gap_a=gaps[side], width=2))
        end.show(t0 + 0.5, 0.3, dy=0, scale_from=0.3)
        label, value = coord_info[side]
        align = {"left": "left", "right": "right"}.get(side, "center")
        sprite = k.info(label, value, align, 40 if side in ("left", "right") else 46)
        ex, ey = ends[side]
        if side == "left":
            pos = (_left(sprite, 96), ey - sprite.height / 2 - 26)
        elif side == "right":
            pos = (_right(sprite, W - 96), ey - sprite.height / 2 - 26)
        elif side == "top":
            pos = (ex, ey - sprite.height / 2 - 28)
        else:
            pos = (ex, ey + sprite.height / 2 + 28)
        info = stage.node(sprite, *pos, z=4)
        info.show(t0 + 0.45, 0.6, dy=16 if side != "top" else -16)
        coord_nodes += [end, info]

    # ---- 0:10–0:14 WHERE IT CAME FROM ----------------------------------------
    stage.camera.animate(10.0, 0.9, "ease_in_out", cy=1230, zoom=0.7)
    frag = objects.city_fragment(340, 230, p)
    frag_c = (790, 1800)
    fragment = stage.node(frag, *frag_c, z=2)
    fragment.show(10.7, 0.7, dy=24, scale_from=0.96)
    pin = stage.node(k.dot(2), frag_c[0] - 170 + 0.62 * 340, frag_c[1] - 115 + 0.45 * 230)
    city = stage.node(k.label(tm.city, 28, th.accent, 6), 0, 1712, z=4)
    city.set(0, x=_left(city.sprite, 110))
    city.show(11.1, 0.6)
    studio_words = tm.studio.split()
    split_at = max(1, len(studio_words) // 2)
    studio_sprite = k.stack([k.text("→ " + " ".join(studio_words[:split_at]), 44),
                             k.text(" ".join(studio_words[split_at:]), 44)], "left", 2)
    studio = stage.node(studio_sprite, _left(studio_sprite, 110), 1712 + 26 + studio_sprite.height / 2, z=4)
    studio.show(11.5, 0.7, rise=True)
    recorded = stage.node(k.label(tm.recorded, 22, th.muted), 0, 1712 + 60 + studio_sprite.height, z=4)
    recorded.set(0, x=_left(recorded.sprite, 110))
    recorded.show(12.0, 0.5)
    back = stage.link(pin, hub, th.accent, 12.4, dur=0.9, gap_a=26, gap_b=200, width=2, arrow=True)
    stage.camera.animate(13.3, 0.8, "ease_in_out", cy=900, zoom=1.0)
    for n in (fragment, city, studio, recorded):
        n.hide(13.35, 0.45, dy=10)
    back.t_hide = 13.35

    # ---- 0:14–0:19 PEOPLE BEHIND THE SOUND -----------------------------------
    for n in coord_nodes:
        n.hide(13.85, 0.4, dy=0)
    for link in coord_links:
        link.t_hide = 13.85
    pc = (540, 930)
    pose(14.0, 0.8, *pc, 0.45, 0.32, pc[1] + 0.45 * 200 + 40)
    hub.animate(14.0, 0.8, "ease_in_out", x=pc[0], y=pc[1])
    people_pos = [(540, 500), (300, 1330), (780, 1330)][:len(tm.people)]
    people_nodes = []
    people_links = []
    for i, (person, pos) in enumerate(zip(tm.people, people_pos)):
        t0 = 14.7 + i * 0.8
        size = k.fit([person.name], 44, 440)
        sprite = k.stack([k.text(person.name, size), k.text(person.role, 30, th.muted, "serif_italic")], "center", 4)
        node = stage.node(sprite, *pos, z=4)
        anchor = stage.node(k.dot(2), *pos)
        people_links.append(stage.link(hub, anchor, line_c, t0, dur=0.5, gap_a=150 if pos[1] < pc[1] else 215,
                                       gap_b=sprite.height / 2 + 26))
        node.show(t0 + 0.35, 0.6, dy=14)
        people_nodes += [node, anchor]
    anchors = people_nodes[1::2]
    for i in range(len(anchors)):
        if len(anchors) == 3:
            a, b = anchors[i], anchors[(i + 1) % 3]
            people_links.append(stage.link(a, b, line_c, 17.0 + i * 0.15, dur=0.5, gap_a=150, gap_b=150,
                                           width=1, dash=6, opacity=0.8))
    beginning_size = k.fit([tm.people_outro], 58, 900, "display_italic")
    beginning = stage.node(k.text(tm.people_outro, beginning_size, th.accent, "display_italic"), 540, 1500, z=5)
    beginning.show(17.65, 0.7, rise=True)

    # ---- 0:19–0:25 MUSICIANS (on the beat) -----------------------------------
    for n in people_nodes + [beginning]:
        n.hide(18.75, 0.4, dy=0)
    for link in people_links:
        link.t_hide = 18.75
    sleeve.hide(18.9, 0.5, dy=0)
    mc = (540, 880)
    vinyl.animate(18.9, 0.8, "ease_in_out", x=540, y=800, scale=0.3)
    title.animate(18.9, 0.8, "ease_in_out", x=540, y=930, scale=0.5)
    hub.animate(18.9, 0.8, "ease_in_out", x=mc[0], y=mc[1])
    slots = [(280, 640), (800, 640), (800, 1230), (540, 1460), (280, 1230), (540, 410)]
    musician_text: dict[str, Node] = {}
    musician_icon: dict[str, Node] = {}
    musician_links = []
    step = 1.5 * beat
    for i, (m, (x, y)) in enumerate(zip(tm.musicians, slots)):
        t0 = 19.4 + i * step
        icon = stage.node(objects.instrument(m.texture, 92, th.foreground, th.accent), x, y - 72, z=4)
        name_size = k.fit([m.name], 36, 360)
        text_sprite_ = k.stack([k.label(m.instrument, 22), k.text(m.name, name_size)], "center", 4)
        text = stage.node(text_sprite_, x, y + 26 + text_sprite_.height / 2 - 20, z=4)
        anchor = stage.node(k.dot(2), x, y)
        dx, dy = x - mc[0], y - mc[1]
        gap_a = 175 if dy < -200 and abs(dx) < 50 else 130
        musician_links.append(stage.link(hub, anchor, line_c, t0, dur=0.6 * beat, gap_a=gap_a, gap_b=115,
                                         easing="ease_out"))
        icon.show(t0 + 0.6 * beat, 0.5, dy=0, scale_from=0.9)
        text.show(t0 + 0.8 * beat, 0.5, dy=12)
        musician_text[m.instrument] = text
        musician_icon[m.instrument] = icon

    # ---- 0:25–0:29 THE TURN --------------------------------------------------
    t_turn = 24.9
    for name, node in musician_text.items():
        if name not in tm.core:
            node.hide(t_turn, 0.45, dy=0)
    for node in musician_icon.values():
        node.hide(t_turn, 0.45, dy=0)
    for link in musician_links:
        link.t_hide = t_turn
    vinyl.hide(t_turn, 0.45, dy=0)
    title.hide(t_turn, 0.45, dy=0)
    left_core, right_core = musician_text[tm.core[0]], musician_text[tm.core[1]]
    left_core.animate(25.0, 0.9, "ease_in_out", x=290, y=1150)
    right_core.animate(25.0, 0.9, "ease_in_out", x=800, y=1150)
    turn_size = k.fit(tm.turn_text, 80, 920)
    turn_lines = [stage.node(k.text(line, turn_size), 540, 440 + i * turn_size * 1.12, z=5)
                  for i, line in enumerate(tm.turn_text)]
    for i, n in enumerate(turn_lines):
        n.show(25.25 + i * 0.3, 0.75, rise=True)
    kit = stage.node(objects.drum_kit(380, 300, th.foreground, th.accent), 290, 880, z=3)
    kit.show(25.9, 0.7, dy=24)
    bass = stage.node(objects.bass_guitar(170, 400, th.foreground, th.accent), 800, 850, z=3)
    bass.show(26.3, 0.7, dy=24)
    pair = stage.node(k.text(tm.turn_pair or " × ".join(tm.core), 54), 540, 1310, z=5)
    pair.show(26.8, 0.6, dy=14)
    pulse_nodes = []
    xs = [330 + i * 140 for i in range(4)]
    t_pulse = 27.2
    for i, x in enumerate(xs):
        d = stage.node(k.dot(22), x, 1420, z=5)
        d.show(t_pulse + i * 0.08, 0.3, dy=0, scale_from=0.3)
        d.pulse = (t_pulse + 0.4 + i * beat, 28.9, 4 * beat, 0.7)
        pulse_nodes.append(d)
        if i < 3:
            dash = stage.node(shapes.rule(70, 2, line_c), x + 70, 1420, z=4)
            dash.show(t_pulse + i * 0.08 + 0.1, 0.3, dy=0)
            pulse_nodes.append(dash)

    # ---- 0:29–0:33 AFTERLIFE -------------------------------------------------
    for n in turn_lines + [kit, bass, pair, left_core, right_core] + pulse_nodes:
        n.hide(28.9, 0.4, dy=0)
    ac = (540, 880)
    vinyl.set(29.0, x=540, y=760, scale=0.3)
    vinyl.show(29.1, 0.6, dy=0, scale_from=0.9)
    title.set(29.0, x=540, y=880, scale=0.55)
    title.show(29.2, 0.6, dy=0)
    hub.set(29.0, x=ac[0], y=ac[1] + 20)
    nq_size = k.fit([tm.afterlife_question], 66, 900, "display_italic")
    next_q = stage.node(k.text(tm.afterlife_question, nq_size, th.foreground, "display_italic"), 540, 420, z=5)
    next_q.show(29.3, 0.7, rise=True)
    caption = stage.node(k.label(f"{tm.track} → {tm.afterlife_caption}", 20, th.accent, 4), 540, 510, z=5)
    caption.show(29.7, 0.5)
    after_pos = [(260, 1240), (540, 1400), (820, 1240)][:len(tm.afterlife)]
    after_nodes = []
    after_links = []
    for i, (item, pos) in enumerate(zip(tm.afterlife, after_pos)):
        t0 = 30.05 + i * 1.5 * beat
        size = k.fit([item.artist], 40, 470)
        sprite = k.stack([k.text(item.artist, size), k.label(item.year, 26)], "center", 6)
        node = stage.node(sprite, *pos, z=4)
        anchor = stage.node(k.dot(2), *pos)
        after_links.append(stage.link(hub, anchor, th.accent, t0, dur=0.55, gap_a=80,
                                      gap_b=sprite.height / 2 + 30, arrow=True))
        node.show(t0 + 0.4, 0.6, dy=14)
        after_nodes += [node]

    # ---- 0:33–0:37 INFLUENCE (zoom out, the whole map) -----------------------
    for n in [next_q, caption] + after_nodes:
        n.hide(32.75, 0.4, dy=0)
    for link in after_links:
        link.t_hide = 32.75
    stage.camera.set(32.9, cx=540, cy=880)
    stage.camera.animate(33.0, 1.4, "ease_in_out", zoom=0.62)
    stage.camera.animate(34.4, 2.5, "linear", zoom=0.58)
    title.animate(33.0, 1.4, "ease_in_out", y=900, scale=0.85)
    vinyl.animate(33.0, 1.4, "ease_in_out", y=740, scale=0.45)
    hub.set(33.0, x=540, y=880)
    influence_nodes = []
    influence_links = []
    for i, name in enumerate(tm.influence_inner):
        a = -math.pi / 2 + i * 2 * math.pi / len(tm.influence_inner)
        pos = (540 + 390 * math.cos(a), 880 + 600 * math.sin(a))
        node = stage.node(k.label(name, 30, th.foreground, 3), *pos, z=4)
        t0 = 33.4 + i * 0.12
        influence_links.append(stage.link(hub, node, line_c, t0, dur=0.45, gap_a=170, gap_b=30, width=2))
        node.show(t0 + 0.3, 0.45, dy=0, scale_from=0.9)
        influence_nodes.append(node)
    for i, name in enumerate(tm.influence_outer):
        a = -math.pi / 2 + math.pi / len(tm.influence_outer) + i * 2 * math.pi / len(tm.influence_outer)
        pos = (540 + 700 * math.cos(a), 880 + 1000 * math.sin(a))
        node = stage.node(k.text(name, 48, th.accent, "display_italic"), *pos, z=4)
        t0 = 34.9 + i * 0.14
        influence_links.append(stage.link(hub, node, line_c, t0, dur=0.55, gap_a=170, gap_b=50, width=1,
                                          dash=5, opacity=0.7))
        node.show(t0 + 0.35, 0.5, dy=0, scale_from=0.9)
        influence_nodes.append(node)

    # ---- 0:37–0:40 FINAL ---------------------------------------------------------
    for n in influence_nodes:
        n.hide(36.9, 0.45, dy=0)
    for link in influence_links:
        link.t_hide = 36.9
    title.hide(36.9, 0.45, dy=0)
    stage.camera.animate(37.0, 0.9, "ease_in_out", cx=540, cy=900, zoom=1.0)
    vinyl.animate(37.0, 0.9, "ease_in_out", x=540, y=760, scale=0.42)
    outro_size = k.fit(tm.outro, 86, 920)
    outro = [stage.node(k.text(line, outro_size), 540, 1010 + i * outro_size * 1.15, z=5, fixed=True)
             for i, line in enumerate(tm.outro)]
    for i, n in enumerate(outro):
        n.show(37.45 + i * 0.3, 0.7, rise=True)
        n.hide(38.65, 0.35, dy=0)
    series = stage.node(k.label(tm.series, 28, th.accent, 8), 540, 990, z=5, fixed=True)
    series.show(38.95, 0.5)
    episode_text = f"№{tm.number:03d} — {tm.track.upper()}"
    ep = stage.node(k.text(episode_text, k.fit([episode_text], 76, 920)), 540, 1075, z=5, fixed=True)
    ep.show(39.05, 0.6, rise=True)
    cta = stage.node(k.text(tm.cta, 38, th.muted, "serif_italic"), 540, 1170, z=5, fixed=True)
    cta.show(39.35, 0.5)

    return stage, _chrome(k, tm, spec)


def _chrome(k: _Kit, tm: TrackMap, spec: VideoSpec):
    """Fixed header (series + episode) and a progress line."""
    sp = k.style.spacing
    th = k.t
    header = Image.new("RGBA", (spec.width, 260), (0, 0, 0, 0))
    left = k.label(tm.series, 20, th.line, 5)
    right = k.label(f"№{tm.number:03d} / {tm.track}", 20, th.line, 5)
    header.alpha_composite(left, (sp.margin_x, sp.header_y))
    header.alpha_composite(right, (spec.width - sp.margin_x - right.width, sp.header_y))
    y = sp.header_y + left.height + 16
    header.paste(th.line, (sp.margin_x, y, spec.width - sp.margin_x, y + 1))
    alpha = header.getchannel("A")

    def overlay(frame: Image.Image, t: float) -> None:
        o = min(1.0, max(0.0, (t - 3.2) / 0.6), max(0.0, (36.9 - t) / 0.5))
        if o > 0.003:
            frame.paste(header, (0, 0), alpha if o >= 0.997 else alpha.point(lambda v: int(v * o)))
        x0, x1 = sp.margin_x, spec.width - sp.margin_x
        frame.paste(th.line, (x0, sp.footer_y, x1, sp.footer_y + 1))
        filled = x0 + int((x1 - x0) * min(t / DURATION, 1.0))
        if filled > x0:
            frame.paste(th.accent, (x0, sp.footer_y - 1, filled, sp.footer_y + 2))

    return overlay
