"""Scene visuals for documentary Reels. Each one fills the visual region (470–1000)
and is chosen by `visual.type` in the scenario. Times are relative to the scene."""

from __future__ import annotations

import math

from PIL import Image, ImageDraw

from prokv.animation.easing import ease
from prokv.graphics import media, objects, shapes, sound
from prokv.layout.documentary.base import (
    CARD_Y, VIS_BOTTOM, VIS_CY, VIS_TOP, SceneContext, card_times, visual,
)
from prokv.layout.maps.base import edge_gap


def _ramp(t: float, t0: float, t1: float, curve: str = "ease_in_out") -> float:
    return ease(curve, (t - t0) / (t1 - t0)) if t1 > t0 else float(t >= t1)


@visual("decade_counter")
def decade_counter(ctx: SceneContext) -> None:
    """1990 counts up to 2000, becomes "1990–2000"; three genre branches hang from a time line.

    visual: {headline, branches: [..], from, to}
    """
    k, s, v = ctx.kit, ctx.s, ctx.scene.visual
    y0, y1 = v.get("from", 1990), v.get("to", 2000)
    size = 230

    def counter(t: float) -> Image.Image:
        p = _ramp(t, s + 0.5, s + 2.5, "ease_in_out")
        return k.text(str(round(y0 + (y1 - y0) * p)), size, k.cream)

    num = ctx.dynamic(counter, 540, 610, z=5)
    num.show(s + 0.15, 0.5, dy=0, scale_from=0.92)
    num.hide(s + 2.75, 0.45, dy=0)
    span = f"{y0}–{y1}"
    big = ctx.node(k.text(span, k.fit([span], 190, 920), k.cream), 540, 610, z=5)
    big.show(s + 2.85, 0.6, dy=0, scale_from=1.12)            # crossfade / morph from the counter
    if v.get("headline"):
        head = k.wrap(v["headline"], k.wrap_fit(v["headline"], 50, 900, 2), 900, k.cream)
        ctx.node(head, 540, 790, z=5).show(s + 3.1, 0.6, rise=True)
    line_y, branch_y = 905, 990
    left, right = ctx.anchor(150, line_y), ctx.anchor(930, line_y)
    ctx.link(left, right, s + 3.3, dur=0.8, width=2)
    branches = v.get("branches", [])
    xs = [150 + (780) * (i + 0.5) / len(branches) for i in range(len(branches))]
    for i, (name, x) in enumerate(zip(branches, xs)):
        t0 = s + 3.6 + i * 0.3
        top = ctx.anchor(x, line_y)
        label = ctx.node(k.label(name, 30, k.cream, 6), x, branch_y, z=5)
        ctx.link(top, label, t0, dur=0.35, gap_b=label.sprite.height / 2 + 8, width=2)
        label.show(t0 + 0.25, 0.5, dy=10)


@visual("rough_wave")
def rough_wave(ctx: SceneContext) -> None:
    """A big year, and a waveform that grows from polished to noisy and uneven.

    visual: {year}
    """
    k, s = ctx.kit, ctx.s
    year = ctx.node(k.text(str(ctx.scene.visual.get("year", "")), 190, k.cream), 540, 575, z=5)
    year.show(s + 0.6, 0.8, dy=0, scale_from=0.8)               # scale for an important date

    def wave(t: float) -> Image.Image:
        return sound.bar_wave(880, 230, t, _ramp(t, s + 1.0, s + 4.8), k.paper)

    ctx.dynamic(wave, 540, 840, z=4).show(s + 0.9, 0.8, dy=0)


@visual("sampling")
def sampling(ctx: SceneContext) -> None:
    """Old record → SAMPLE → new record, joined by drawn lines.

    visual: {from: ["1972", "SOUL & FUNK"], to: ["1995", "HIP-HOP"], label: "SAMPLE"}
    """
    k, s, v = ctx.kit, ctx.s, ctx.scene.visual
    y = 690
    rec = objects.vinyl_record(270, k.p)
    sides = []
    for i, (x, (year, genre)) in enumerate(zip((235, 845), (v["from"], v["to"]))):
        t0 = s + 0.9 + i * 1.6
        r = ctx.node(rec, x, y, z=3)
        r.show(t0, 0.7, dy=0, scale_from=0.9)
        r.spin = (t0, 40.0 if i else 25.0, 0.8)
        cap = k.stack([k.label(year, 30, k.cream, 6), k.label(genre, 22, k.paper, 5)], "center", 8)
        ctx.node(cap, x, y + 200, z=4).show(t0 + 0.3, 0.6, dy=10)
        sides.append(r)
    label = v.get("label", "SAMPLE")
    text = k.label(label, 26, k.cream, 6)
    pill = Image.new("RGBA", (text.width + 56, text.height + 30), (0, 0, 0, 0))
    ImageDraw.Draw(pill).rounded_rectangle((1, 1, pill.width - 2, pill.height - 2), radius=pill.height // 2,
                                           fill=k.dark_olive, outline=k.paper, width=2)
    pill.alpha_composite(text, (28, 15))
    mid = ctx.node(pill, 540, y, z=5)
    mid.show(s + 1.9, 0.5, dy=0, scale_from=0.85)
    ctx.link(sides[0], mid, s + 1.6, dur=0.5, gap_a=145, gap_b=pill.width / 2 + 10)
    ctx.link(mid, sides[1], s + 2.3, dur=0.5, gap_a=pill.width / 2 + 10, gap_b=145, arrow=True)


@visual("europe_map")
def europe_map(ctx: SceneContext) -> None:
    """Dot-matrix Europe; pulsing lines between music centres; genre words around it.

    visual: {words: [..], bpm}
    """
    k, s, v = ctx.kit, ctx.s, ctx.scene.visual
    w, h = 640, 470
    cx, cy = 540, VIS_CY + 10
    dots = media.europe_dots(w, h, k.paper)
    dots.putalpha(dots.getchannel("A").point(lambda a: a * 45 // 100))   # a soft tint of paper
    ctx.node(dots, cx, cy, z=2).show(s + 0.5, 0.9, dy=0)
    beat = 60 / v.get("bpm", 128)
    centres = []
    for i, (fx, fy) in enumerate(media.EUROPE_CENTRES):
        dot = ctx.node(k.dot(14, k.cream), cx - w / 2 + fx * w, cy - h / 2 + fy * h, z=4)
        dot.show(s + 1.0 + i * 0.12, 0.4, dy=0, scale_from=0.3)
        dot.pulse = (s + 1.6 + (i % 2) * beat, ctx.e, 2 * beat, 0.6)
        centres.append(dot)
    pairs = [(0, 1), (1, 2), (1, 3), (3, 4), (3, 5), (2, 5), (0, 2)]
    for j, (a, b) in enumerate(pairs):
        ctx.link(centres[a], centres[b], s + 1.3 + j * 0.12, dur=0.5, gap_a=10, gap_b=10, width=2, opacity=0.85)
    spots = [(215, VIS_TOP + 40), (865, VIS_TOP + 120), (540, VIS_BOTTOM - 10)]
    for i, (word, (x, y)) in enumerate(zip(v.get("words", []), spots)):
        ctx.node(k.label(word, 30, k.cream, 7), x, y, z=5).show(s + 1.9 + i * 0.35, 0.5, dy=10)


@visual("voice_wave")
def voice_wave(ctx: SceneContext) -> None:
    """A calm voice line and two dates compared on a small scale, timed with the cards.

    visual: {marks: ["1992", "1997"]}
    """
    k, s, sc = ctx.kit, ctx.s, ctx.scene

    def line(t: float) -> Image.Image:
        return sound.voice_line(880, 250, t, k.cream, calm=0.7)

    ctx.dynamic(line, 540, 660, z=4).show(s + 0.8, 1.2, dy=0, easing="ease_in_out")
    y = 900
    x0, x1 = 200, 880
    ctx.link(ctx.anchor(x0, y), ctx.anchor(x1, y), s + 1.4, dur=1.0, width=2)
    marks = sc.visual.get("marks", [])
    times = card_times(sc) or [s + 2.5 + i for i in range(len(marks))]
    for i, (mark, t) in enumerate(zip(marks, times)):
        x = x0 + (x1 - x0) * (0.2 + 0.6 * i)
        ctx.node(k.dot(16, k.cream), x, y, z=5).show(t, 0.8, dy=0, scale_from=0.3, easing="ease_in_out")
        ctx.node(k.text(mark, 64, k.cream), x, y - 70, z=5).show(t + 0.15, 1.0, dy=12, easing="ease_in_out")


@visual("split")
def split(ctx: SceneContext) -> None:
    """Two halves in contrast; genre words give way to the music cards of each side.

    visual: {left: "BRITPOP", right: "POP"} — the scene's two cards go left and right.
    """
    k, s, sc = ctx.kit, ctx.s, ctx.scene
    v = sc.visual
    h = VIS_BOTTOM - VIS_TOP
    panel = Image.new("RGBA", (444, h), k.p.dark_burgundy)
    ImageDraw.Draw(panel).rectangle((0, 0, 443, 6), fill=k.olive)
    ctx.node(panel, 96 + 222, VIS_TOP + h / 2, z=1).show(s + 0.4, 0.8, dy=0)
    outline = Image.new("RGBA", (444, h), (0, 0, 0, 0))
    ImageDraw.Draw(outline).rectangle((1, 1, 442, h - 2), outline=k.paper, width=2)
    ctx.node(outline, 984 - 222, VIS_TOP + h / 2, z=1).show(s + 0.7, 0.8, dy=0)
    words = []
    for i, (word, x) in enumerate(((v["left"], 318), (v["right"], 762))):
        size = k.fit([word], 76, 380)
        n = ctx.node(k.text(word, size, k.cream if i == 0 else k.paper), x, VIS_CY, z=4)
        n.show(s + 0.9 + i * 0.4, 0.6, dy=0, scale_from=0.94)
        words.append(n)
    for i, (card, t, x) in enumerate(zip(sc.cards, card_times(sc), (318, 762))):
        words[i].hide(t - 0.3, 0.4, dy=-20)
        n = ctx.node(k.card(card, width=420), x, VIS_CY, z=5)
        n.show(t, 0.6, dy=24)


@visual("flow")
def flow(ctx: SceneContext) -> None:
    """A vertical chain (DISCO ↓ SAMPLING ↓ HOUSE) and a spinning record, moving on the beat.

    visual: {steps: [..], bpm}
    """
    k, s, v = ctx.kit, ctx.s, ctx.scene.visual
    beat = 60 / v.get("bpm", 124)
    steps = v["steps"]
    ys = [VIS_TOP + 80 + i * (VIS_BOTTOM - VIS_TOP - 160) / max(len(steps) - 1, 1) for i in range(len(steps))]
    prev = None
    for i, (step, y) in enumerate(zip(steps, ys)):
        t0 = s + 0.9 + i * 2 * beat
        n = ctx.node(k.text(step, k.fit([step], 60, 520), k.cream if i == len(steps) - 1 else k.paper), 330, y)
        ctx.slide_in(n, t0, dx=-60, dur=0.5)
        if prev is not None:
            ctx.link(prev, n, t0 - 0.3, dur=0.35, gap_a=prev.sprite.height / 2 + 12,
                     gap_b=n.sprite.height / 2 + 12, arrow=True)
        prev = n
    rec = ctx.node(objects.vinyl_record(300, k.p), 800, VIS_CY, z=3)
    rec.show(s + 0.7, 0.7, dy=0, scale_from=0.9)
    rec.spin = (s + 0.7, 200.0, 1.2)                      # 33⅓ rpm
    rec.pulse = (s + 1.5, ctx.e, beat, 0.025)


@visual("autotune")
def autotune(ctx: SceneContext) -> None:
    """A natural pitch line snaps to note lanes; VOICE → PROCESSING → NEW SOUND; AUTO-TUNE 1998.

    visual: {headline, year, chain: [..], morph_at: [start, end]}
    """
    k, s, v = ctx.kit, ctx.s, ctx.scene.visual
    m0, m1 = v.get("morph_at", [3.0, 5.6])

    def pitch(t: float) -> Image.Image:
        return sound.pitch_correction(880, 280, t, _ramp(t, s + m0, s + m1), k.cream, k.olive)

    ctx.dynamic(pitch, 540, 735, z=4).show(s + 0.8, 0.8, dy=0)
    chain = v.get("chain", [])
    xs = [200 + 680 * i / max(len(chain) - 1, 1) for i in range(len(chain))]
    beats = [s + 1.0, s + m0 + 0.2, s + m1 + 0.2]
    prev = None
    for i, (word, x) in enumerate(zip(chain, xs)):
        n = ctx.node(k.label(word, 22, k.cream if i == len(chain) - 1 else k.paper, 4), x, 925, z=5)
        n.show(beats[min(i, 2)], 0.5, dy=10)
        if prev is not None:
            ctx.link(prev, n, beats[min(i, 2)] - 0.25, dur=0.3, gap_a=edge_gap(prev.sprite, 1, 0),
                     gap_b=edge_gap(n.sprite, 1, 0), arrow=True)
        prev = n
    head = v.get("headline", "AUTO-TUNE")
    ctx.node(k.text(head, k.fit([head], 96, 700), k.cream), 450, 540, z=5).show(s + m1 + 0.3, 0.7, rise=True)
    if v.get("year"):
        ctx.node(k.label(str(v["year"]), 36, k.paper, 8), 870, 548, z=5).show(s + m1 + 0.6, 0.6, dy=0,
                                                                               scale_from=0.8)


@visual("formats")
def formats(ctx: SceneContext) -> None:
    """VINYL → CASSETTE → CD → MP3, then 1999 → 2000 with the last digit growing.

    visual: {from_year, to_year, years_at}
    """
    k, s, v = ctx.kit, ctx.s, ctx.scene.visual
    y = 600
    icons = [
        ("VINYL", objects.vinyl_record(140, k.p)),
        ("CASSETTE", media.cassette(170, k.cream, k.olive)),
        ("CD", media.compact_disc(140, k.cream, k.olive)),
        ("MP3", media.mp3_file(118, k.cream, k.paper, k.fonts.get("mono", 26))),
    ]
    xs = [165, 400, 640, 900]
    nodes = []
    for i, ((name, sprite), x) in enumerate(zip(icons, xs)):
        t0 = s + 0.8 + i * 0.7
        n = ctx.node(sprite, x, y, z=4)
        n.show(t0, 0.5, dy=16)
        ctx.node(k.label(name, 20, k.paper, 5), x, y + 110, z=4).show(t0 + 0.15, 0.4, dy=8)
        if nodes:
            ctx.link(nodes[-1], n, t0 - 0.3, dur=0.3, gap_a=edge_gap(nodes[-1].sprite, 1, 0) - 4,
                     gap_b=edge_gap(n.sprite, 1, 0) - 4, arrow=True)
        nodes.append(n)
    t_years = s + v.get("years_at", 4.4)
    for n in nodes:
        n.animate(t_years, 0.6, "ease_in_out", opacity=0.35)
    old, new = str(v.get("from_year", 1999)), str(v.get("to_year", 2000))
    a = ctx.node(k.text(old, 120, k.paper), 300, 860, z=5)
    a.show(t_years, 0.6, dy=0, scale_from=0.9)
    arrow = ctx.node(shapes.arrow(110, k.cream, thickness=3, head=16, direction="right"), 540, 860, z=5)
    arrow.show(t_years + 0.3, 0.4, dy=0)
    b = ctx.node(k.text(new, 120, k.cream), 780, 860, z=5)
    b.show(t_years + 0.5, 0.6, dy=0, scale_from=0.9)
    b.animate(t_years + 1.3, 0.8, "ease_in_out", scale=1.22)  # the new year grows


@visual("finale")
def finale(ctx: SceneContext) -> None:
    """Everything has cleared; one large heading, the question, the call to comment.

    visual: {headline, question, cta}
    """
    k, s, v = ctx.kit, ctx.s, ctx.scene.visual
    head = v.get("headline", "")
    ctx.node(k.text(head, k.fit([head], 190, 920), k.cream), 540, 700, z=5).show(s + 0.3, 0.8, rise=True)
    if v.get("question"):
        q = k.wrap(v["question"], k.wrap_fit(v["question"], 56, 920, 3), 920, k.cream)
        ctx.node(q, 540, 900 + q.height / 2, z=5).show(s + 0.9, 0.7, rise=True)
    if v.get("cta"):
        ctx.node(k.label(v["cta"], 28, k.paper, 8), 540, CARD_Y + 60, z=5).show(s + 1.6, 0.6, dy=10)
