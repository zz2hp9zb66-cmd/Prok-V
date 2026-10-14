"""The seven scene layouts of a photo-led design documentary (Blue Note covers).

All moments are fractions of the scene length (ctx.at), so scenes stay in sync
when their length follows the actual speech. Text is placed next to images, not
over the key parts of original covers.
"""

from __future__ import annotations

from prokv.graphics.imageview import FULL
from prokv.layout.image_story.base import StoryContext, layout


def _swap(ctx: StoryContext, old, new_t: float, dur: float = 0.4) -> None:
    """Crossfade: the old node fades out while the next one fades in."""
    if old is not None:
        old.hide(new_t + dur * 0.5, dur, dy=0)


def _caption(ctx: StoryContext, text: str, y: float, t: float, color: str, x: float = 80, size: int = 26):
    lab = ctx.kit.label(text, size, color, 4, bold=True)
    n = ctx.text(lab, x + lab.width / 2, y, text)
    n.show(t, 0.5, dy=10)
    return n


def _region(ctx: StoryContext, image_id: str, name: str):
    return ctx.story.images[image_id].regions.get(name)


def _album_card(ctx: StoryContext, image_id: str, x: float, y: float, t: float, align: str = "left"):
    k, img = ctx.kit, ctx.story.images[image_id]
    sprite = k.stack([k.label(img.artist, 26, k.blue, 4, bold=True), k.text(img.album, 58, k.ink),
                      k.label(img.year, 28, k.olive, 6, bold=True)], align, 10)
    n = ctx.text(sprite, x + sprite.width / 2 if align == "left" else x, y + sprite.height / 2,
                 f"{img.artist} {img.album} {img.year}")
    ctx_slide(n, t)
    return n


def ctx_slide(n, t: float, dx: float = 70) -> None:
    x = n.value(t)["x"]
    n.set(t, x=x + dx, opacity=0.0)
    n.animate(n.keys[-1].t, 0.6, "ease_out_quart", x=x, opacity=1.0)


@layout("hook")
def hook(ctx: StoryContext) -> None:
    """Fast, calm detail shots of three covers → the collage → BLUE NOTE + question."""
    k, sc = ctx.kit, ctx.scene
    W, H, cy = 1080, 900, 700
    details = [("01", "legs", "CROP"), ("02", "blue", "TYPE"), ("03", "clock", "CONCEPT")]
    marks = [0.0, 0.2, 0.4, 0.6]
    prev = None
    for (image_id, region, tag), (a, b) in zip(details, zip(marks, marks[1:])):
        box = _region(ctx, image_id, region) or FULL
        wide = (max(0, box[0] - 0.06), max(0, box[1] - 0.06), min(1, box[2] + 0.06), min(1, box[3] + 0.06))
        win = ctx.window(image_id, 540, cy, W, H, [(ctx.at(a), box), (ctx.at(b) + 0.4, wide)])
        win.node.show(ctx.at(a), 0.4, dy=0)
        _swap(ctx, prev, ctx.at(a))
        chip = ctx.tag(tag, 80, cy + H / 2 - 70, ctx.at(a) + 0.3, k.cream, k.ink)
        chip.hide(ctx.at(b) + 0.1, 0.3, dy=0)
        prev = win.node
    collage = ctx.window("08", 540, cy, W, H, [(ctx.at(0.6), FULL), (ctx.e, (0.06, 0.06, 0.94, 0.94))])
    collage.node.show(ctx.at(0.6), 0.5, dy=0)
    _swap(ctx, prev, ctx.at(0.6))
    texts = sc.texts
    _caption(ctx, texts.get("kicker", ""), 1190, ctx.at(0.62), k.blue)
    x = 80
    for i, word in enumerate(texts.get("headline", "BLUE NOTE").split()):
        sprite = k.text(word, 150, k.ink)
        n = ctx.text(sprite, x + sprite.width / 2, 1280, word)
        n.show(ctx.at(0.64) + i * 0.18, 0.6, rise=True)
        x += sprite.width + 30
    q = k.wrap(texts.get("question", ""), 44, 900, k.ink, bold=True)
    ctx.text(q, 80 + q.width / 2, 1385 + q.height / 2, texts.get("question", "")).show(ctx.at(0.74), 0.6, dy=12)


@layout("camera")
def camera(ctx: StoryContext) -> None:
    """Wolff & Lion → a session portrait (slow push-in) → the contact sheet, then one frame."""
    k, sc = ctx.kit, ctx.scene
    cy = 715
    a = ctx.window("05", 540, cy, 900, 900, [(ctx.s, FULL), (ctx.at(0.36), (0.03, 0.03, 0.97, 0.97))])
    a.node.show(ctx.s + 0.1, 0.6, dy=0)
    cap_a = _caption(ctx, ctx.story.images["05"].caption, 1195, ctx.at(0.08), k.ink)
    face = _region(ctx, "06", "face") or (0.2, 0.08, 0.75, 0.62)
    b = ctx.window("06", 540, cy, 900, 900, [(ctx.at(0.34), FULL), (ctx.at(0.66), face)])
    b.node.show(ctx.at(0.34), 0.5, dy=0)
    _swap(ctx, a.node, ctx.at(0.34))
    cap_a.hide(ctx.at(0.34), 0.3, dy=0)
    cap_b = _caption(ctx, ctx.story.images["06"].caption, 1195, ctx.at(0.38), k.ink)
    cell = _region(ctx, "07", "frame") or (0.33, 0.27, 0.67, 0.52)
    c = ctx.window("07", 540, cy, 720, 900, [(ctx.at(0.64), FULL), (ctx.at(0.80), FULL), (ctx.at(0.98), cell)])
    c.node.show(ctx.at(0.64), 0.5, dy=0)
    _swap(ctx, b.node, ctx.at(0.64))
    cap_b.hide(ctx.at(0.64), 0.3, dy=0)
    _caption(ctx, ctx.story.images["07"].caption, 1195, ctx.at(0.68), k.ink)
    x = 80
    for i, word in enumerate(sc.texts.get("tags", [])):
        lab = k.label(word, 21, k.blue, 3, bold=True)
        ctx.text(lab, x + lab.width / 2, 1262, word).show(ctx.at(0.2 + 0.25 * i), 0.5, dy=8)
        x += lab.width + 22
        if i < len(sc.texts["tags"]) - 1:
            ctx.line((x - 12, 1250), (x - 12, 1274), ctx.at(0.2 + 0.25 * i) + 0.2, k.muted, dur=0.2)
            x += 10
    if sc.facts:
        fact = k.wrap(sc.facts[0], 30, 900, k.ink)
        ctx.text(fact, 80 + fact.width / 2, 1325 + fact.height / 2, sc.facts[0]).show(ctx.at(0.5), 0.6, dy=10)


@layout("designer")
def designer(ctx: StoryContext) -> None:
    """Portrait + REID / MILES on a blue panel → Cool Struttin' annotated → Midnight Blue type sizes."""
    k, sc = ctx.kit, ctx.scene
    t = sc.texts
    photo_box = _region(ctx, "04", "photo") or FULL
    portrait = ctx.window("04", 332, 640, 504, 672, [(ctx.s, photo_box), (ctx.at(0.4), photo_box)],
                          reveal=(ctx.s + 0.1, ctx.s + 0.9, "up"))
    portrait.node.show(ctx.s + 0.05, 0.2, dy=0)
    panel = ctx.node(k.block(420, 672, k.blue), 810, 640, z=1)
    panel.set(ctx.s, x=810 + 440, opacity=1.0)
    panel.animate(ctx.s + 0.2, 0.7, "ease_out_quart", x=810)
    for i, word in enumerate(t.get("name", ["REID", "MILES"])):
        sprite = k.text(word, 112, k.cream)
        ctx.text(sprite, 630 + sprite.width / 2, 400 + i * 120, word).show(ctx.s + 0.7 + i * 0.25, 0.6, rise=True)
    role = k.label(t.get("role", ""), 24, k.muted, 4, bold=True)
    ctx.text(role, 632 + role.width / 2, 650, t.get("role", "")).show(ctx.s + 1.3, 0.5, dy=8)
    years = k.text(t.get("years", ""), 64, k.cream)
    ctx.text(years, 632 + years.width / 2, 740, t.get("years", "")).show(ctx.s + 1.5, 0.6, dy=10, scale_from=0.9)
    credit = k.label(ctx.story.images["04"].caption, 18, k.olive, 3)
    ctx.text(credit, 80 + credit.width / 2, 1000, ctx.story.images["04"].caption).show(ctx.s + 1.0, 0.5, dy=0)
    # Editorial transition: the portrait and panel move aside, the cover comes in.
    t_cover = ctx.at(0.4)
    for item in list(ctx.items):
        if hasattr(item, "keys") and item.value(t_cover)["opacity"] > 0:
            item.animate(max(t_cover, item.keys[-1].t), 0.5, "ease_in_out",
                         x=item.value(t_cover)["x"] - 260, opacity=0.0)
    cover = ctx.window("01", 540, 700, 900, 900, [(t_cover, FULL)])
    ctx_slide(cover.node, t_cover + 0.15, dx=200)
    m = ctx.mark()
    notes = [("legs", "CROP", k.blue), ("credits", "TEXT", k.blue), ("space", "SPACE", k.burgundy)]
    for i, (region, tag, color) in enumerate(notes):
        rect = cover.rect_at(_region(ctx, "01", region), t_cover + 1)
        ta = ctx.at(0.47 + 0.07 * i)
        ctx.outline(rect, ta, color)
        ctx.tag(tag, rect[0] + 10, rect[1] + 10, ta + 0.3, k.cream, color, 22)
    t_type = ctx.at(0.7)
    ctx.hide_since(m, t_type - 0.1)
    cover.node.hide(t_type, 0.4, dy=0)
    mb = ctx.window("02", 540, 700, 900, 900, [(t_type, FULL)])
    mb.node.show(t_type + 0.1, 0.5, dy=0)
    for i, (region, tag) in enumerate([("blue", "TITLE"), ("midnight", "SUBTITLE"), ("credits", "CREDITS")]):
        rect = mb.rect_at(_region(ctx, "02", region), t_type + 1)
        ta = t_type + 0.5 + i * 0.45
        ctx.outline(rect, ta, k.cream, width=3)
        ctx.tag(tag, rect[0] + 10, rect[3] - 44, ta + 0.3, k.ink, k.cream, 20)
    big = k.text(t.get("fact_big", ""), 92, k.blue)
    ctx.text(big, 80 + big.width / 2, 1225, t.get("fact_big", "")).show(ctx.at(0.45), 0.7, dy=0, scale_from=0.85)
    small = k.label(t.get("fact_label", ""), 24, k.ink, 4, bold=True)
    ctx.text(small, 100 + big.width + small.width / 2, 1240, t.get("fact_label", "")).show(ctx.at(0.48), 0.5, dy=6)
    if sc.facts:
        fact = k.wrap(sc.facts[0], 30, 900, k.ink)
        ctx.text(fact, 80 + fact.width / 2, 1310 + fact.height / 2, sc.facts[0]).show(ctx.at(0.52), 0.6, dy=8)


@layout("formula")
def formula(ctx: StoryContext) -> None:
    """TYPOGRAPHY (02) → PHOTOGRAPHY (01) → COMPOSITION (03) → a three-cover gallery."""
    k, sc = ctx.kit, ctx.scene
    blocks = [("02", sc.texts["words"][0], [("blue", k.cream), ("midnight", k.cream), ("credits", k.cream)]),
              ("01", sc.texts["words"][1], [("legs", k.blue), ("space", k.burgundy)]),
              ("03", sc.texts["words"][2], [("clock", k.cream), ("door", k.cream)])]
    spans = [(0.0, 0.29), (0.29, 0.58), (0.58, 0.84)]
    prev_win = prev_word = None
    m = ctx.mark()
    for (image_id, word, notes), (a, b) in zip(blocks, spans):
        ta = ctx.at(a)
        if prev_win is not None:
            ctx.hide_since(m, ta - 0.1)   # the previous block (cover, heading, lines) leaves
        m = ctx.mark()
        size = k.fit([word], 104, 920)
        head = ctx.text(k.text(word, size, k.ink), 540, 330, word)
        head.show(ta + 0.1, 0.6, rise=True)
        win = ctx.window(image_id, 540, 860, 860, 860, [(ta, FULL), (ctx.at(b) + 0.4, (0.02, 0.02, 0.98, 0.98))])
        win.node.show(ta + 0.05, 0.45, dy=0)
        _swap(ctx, prev_win, ta)
        for i, (region, color) in enumerate(notes):
            rect = win.rect_at(_region(ctx, image_id, region), ta + 0.5)
            ctx.outline(rect, ta + 0.6 + i * 0.5, color, width=4)
        if image_id == "02":  # reading path: credits → midnight → blue
            pts = [win.rect_at(_region(ctx, "02", r), ta + 0.5) for r in ("credits", "midnight", "blue")]
            centres = [((r[0] + r[2]) / 2, (r[1] + r[3]) / 2) for r in pts]
            for j, (p, q) in enumerate(zip(centres, centres[1:])):
                ctx.line(p, q, ta + 1.9 + j * 0.3, k.muted, dur=0.35, width=4, arrow=True)
        prev_win, prev_word = win.node, head
    tg = ctx.at(0.84)
    ctx.hide_since(m, tg - 0.1)
    prev_win.hide(tg, 0.35, dy=0)
    prev_word.hide(tg, 0.35, dy=0)
    for i, (image_id, word) in enumerate(zip(("02", "01", "03"), sc.texts["words"])):
        x = 200 + 340 * i
        win = ctx.window(image_id, x, 820, 300, 300, [(tg, FULL)])
        ctx_slide(win.node, tg + 0.15 * i, dx=120)
        lab = k.label(word, 22, k.ink, 3, bold=True)
        ctx.text(lab, x, 1000, word).show(tg + 0.3 + 0.15 * i, 0.4, dy=6)
    if sc.texts.get("note"):
        note = k.wrap(sc.texts["note"], 28, 900, k.olive)
        ctx.text(note, 80 + note.width / 2, 1330 + note.height / 2, sc.texts["note"]).show(tg + 0.6, 0.5, dy=6)


@layout("system")
def system(ctx: StoryContext) -> None:
    """Three covers one by one with album cards → side by side, lines to shared qualities."""
    k, sc = ctx.kit, ctx.scene
    ids = ["01", "02", "03"]
    prev = prev_card = None
    for i, image_id in enumerate(ids):
        ta = ctx.at(0.02 + 0.17 * i)
        win = ctx.window(image_id, 540, 640, 760, 760, [(ta, FULL), (ctx.at(0.19 + 0.17 * i) + 0.4,
                                                                    (0.03, 0.03, 0.97, 0.97))])
        ctx_slide(win.node, ta, dx=160)
        _swap(ctx, prev, ta)
        card = _album_card(ctx, image_id, 160, 1085, ta + 0.3)
        if prev_card is not None:
            prev_card.hide(ta, 0.3, dy=0)
        prev, prev_card = win.node, card
    tr = ctx.at(0.54)
    prev.hide(tr, 0.35, dy=0)
    prev_card.hide(tr, 0.35, dy=0)
    xs = [200, 540, 880]
    for i, image_id in enumerate(ids):
        win = ctx.window(image_id, xs[i], 560, 300, 300, [(tr, FULL)])
        ctx_slide(win.node, tr + 0.12 * i, dx=100)
        ctx.line((xs[i], 715), (xs[i], 790), tr + 0.7 + 0.1 * i, k.blue, dur=0.3)
    ctx.line((200, 790), (880, 790), tr + 0.9, k.blue, dur=0.5)
    qualities = sc.texts.get("qualities", [])
    for i, q in enumerate(qualities):
        col, row = i % 2, i // 2
        x, y = 80 + col * 470, 845 + row * 70
        ctx.line((x + 10, 790), (x + 10, y - 14), tr + 1.3 + 0.15 * i, k.muted, dur=0.25)
        ctx.tag(q, x, y - 14, tr + 1.45 + 0.15 * i, k.cream, k.blue, 22)
    final = sc.texts.get("final", [])
    for i, line in enumerate(final):
        sprite = k.text(line, k.fit([line], 74, 920), k.ink if i == 0 else k.blue)
        ctx.text(sprite, 80 + sprite.width / 2, 1150 + i * 92, line).show(ctx.at(0.8) + 0.25 * i, 0.6, rise=True)


@layout("legacy")
def legacy(ctx: StoryContext) -> None:
    """The collage → a flat, clearly illustrative gallery wall with the three covers."""
    k, sc = ctx.kit, ctx.scene
    collage = ctx.window("08", 540, 700, 960, 900, [(ctx.s, FULL), (ctx.at(0.38), (0.08, 0.08, 0.92, 0.92))])
    collage.node.show(ctx.s + 0.1, 0.5, dy=0)
    tw = ctx.at(0.36)
    collage.node.hide(tw, 0.45, dy=0)
    wall = ctx.node(k.block(1080, 640, k.muted), 540, 640, z=1)
    wall.show(tw, 0.5, dy=0)
    floor = ctx.node(k.block(1080, 6, k.ink), 540, 963, z=1)
    floor.show(tw + 0.2, 0.4, dy=0)
    for i, (image_id, size, x) in enumerate((("01", 250, 220), ("02", 300, 540), ("03", 250, 860))):
        frame = ctx.node(k.block(size + 36, size + 36, k.ink), x, 640, z=2)
        mat = ctx.node(k.block(size + 20, size + 20, k.cream), x, 640, z=2)
        win = ctx.window(image_id, x, 640, size, size, [(tw, FULL)], z=3)
        for n in (frame, mat, win.node):
            n.show(tw + 0.35 + 0.2 * i, 0.5, dy=-16)
    ctx.tag(sc.texts.get("illustration", "ILLUSTRATION"), 80, 350, tw + 0.5, k.ink, k.cream, 18)
    for i, line in enumerate(sc.texts.get("headline", [])):
        sprite = k.text(line, k.fit([line], 70, 920), k.ink if i == 0 else k.blue)
        ctx.text(sprite, 80 + sprite.width / 2, 1040 + i * 84, line).show(tw + 0.9 + i * 0.25, 0.6, rise=True)
    y = 1200
    for i, fact in enumerate(sc.facts):
        f = k.wrap(fact, 28, 900, k.ink)
        ctx.text(f, 80 + f.width / 2, y + f.height / 2, fact).show(ctx.at(0.6) + 0.5 * i, 0.5, dy=8)
        y += f.height + 22


@layout("finale")
def finale(ctx: StoryContext) -> None:
    """Three covers → the collage → BLUE NOTE / THE ART OF JAZZ → the question → fade."""
    k, sc = ctx.kit, ctx.scene
    wins = []
    for i, (image_id, x) in enumerate(zip(("01", "02", "03"), (200, 540, 880))):
        w = ctx.window(image_id, x, 640, 300, 300, [(ctx.s, FULL)])
        ctx_slide(w.node, ctx.s + 0.1 + 0.15 * i, dx=100)
        wins.append(w.node)
    tc = ctx.at(0.3)
    for n in wins:
        n.hide(tc, 0.4, dy=0)
    collage = ctx.window("08", 540, 640, 1080, 760, [(tc, FULL), (ctx.e, (0.05, 0.05, 0.95, 0.95))])
    collage.node.show(tc, 0.6, dy=0)
    for i, line in enumerate(sc.texts.get("headline", [])):
        size = 140 if i == 0 else 40
        sprite = k.text(line, k.fit([line], size, 920), k.ink if i == 0 else k.blue)
        ctx.text(sprite, 80 + sprite.width / 2, 1110 + i * 110, line).show(ctx.at(0.4) + 0.3 * i, 0.6, rise=True)
    q = sc.texts.get("question", "")
    if q:
        qs = k.wrap(q, 42, 900, k.ink, bold=True)
        ctx.text(qs, 80 + qs.width / 2, 1330 + qs.height / 2, q).show(ctx.at(0.6), 0.6, dy=10)
