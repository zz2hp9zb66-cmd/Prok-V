"""Shared layers of a documentary scene and the scene context.

Screen regions (1080×1920, inside the Reels safe area):
    decade timeline 205 · kicker 300 · title 375 · visual 470–1000 ·
    music card 1130 · fact 1370
Order inside a scene: title → (voice starts) → visual → card 1 → card 2 → fact.
"""

from __future__ import annotations

from typing import Callable

from PIL import Image, ImageDraw

from prokv.animation.stage import DynamicNode, Link, Node, Stage
from prokv.content.documentary import Card, DocScene, Documentary
from prokv.layout.maps.base import Kit

TIMELINE_Y, KICKER_Y, TITLE_Y = 205, 300, 378
VIS_TOP, VIS_BOTTOM = 470, 1000
VIS_CY = (VIS_TOP + VIS_BOTTOM) // 2
CARD_Y, FACT_Y = 1130, 1375
CARD_W = 888

VISUALS: dict[str, Callable[["SceneContext"], None]] = {}


def visual(name: str):
    def register(fn):
        VISUALS[name] = fn
        return fn
    return register


class DocKit(Kit):
    """Kit on the burgundy theme: cream text, paper secondary, olive accents."""

    def __init__(self, style) -> None:
        super().__init__(style)
        self.t = style.themes["burgundy"]
        p = style.palette
        self.cream, self.paper, self.olive, self.dark_olive = p.cream, p.paper, p.olive, p.dark_olive

    def card(self, card: Card, width: int = CARD_W) -> Image.Image:
        """ARTIST (small caps) · TRACK (large) · YEAR, on a dark-olive card.

        Narrow cards (split screens) stack the year under the track instead of beside the artist.
        """
        pad = 34 if width > 600 else 26
        narrow = width <= 600
        artist = self.label(card.artist, 24 if not narrow else 22, self.paper, 5)
        year = self.label(card.year, 30, self.cream, 6)
        inner = width - 2 * pad - 14
        size = self.wrap_fit(card.track, 62 if not narrow else 54, inner, 2)
        track = self.wrap(card.track, size, inner, self.cream, align="left", leading=1.04)
        h = pad + artist.height + 10 + track.height + pad + (year.height + 12 if narrow else 0)
        img = Image.new("RGBA", (width, h), self.dark_olive)
        d = ImageDraw.Draw(img)
        d.rectangle((0, 0, 7, h), fill=self.olive)
        img.alpha_composite(artist, (pad + 14, pad))
        img.alpha_composite(track, (pad + 14, pad + artist.height + 10))
        if narrow:
            img.alpha_composite(year, (pad + 14, pad + artist.height + 10 + track.height + 12))
        else:
            img.alpha_composite(year, (width - pad - year.width, pad - 4))
        return img

    def fact(self, text: str, width: int = CARD_W) -> Image.Image:
        label = self.label("ФАКТ", 22, self.paper, 6)
        body = self.wrap(text, 39, width - 40, self.cream, "serif", align="left", leading=1.22)
        h = label.height + 14 + body.height + 8
        img = Image.new("RGBA", (width, h), (0, 0, 0, 0))
        d = ImageDraw.Draw(img)
        d.rectangle((0, 0, 3, h), fill=self.paper)
        img.alpha_composite(label, (24, 0))
        img.alpha_composite(body, (24, label.height + 14))
        return img


class SceneContext:
    def __init__(self, stage: Stage, kit: DocKit, doc: Documentary, scene: DocScene, index: int) -> None:
        self.stage, self.kit, self.doc, self.scene, self.index = stage, kit, doc, scene, index
        self.s, self.e = scene.start, scene.end
        self.items: list[Node | Link] = []
        self.last = index == len(doc.scenes) - 1

    @property
    def voice_at(self) -> float:
        return self.s + self.doc.narration_lead_s

    def node(self, sprite: Image.Image, x: float, y: float, z: int = 4) -> Node:
        n = self.stage.node(sprite, x, y, z=z)
        self.items.append(n)
        return n

    def dynamic(self, draw, x: float, y: float, z: int = 4) -> DynamicNode:
        n = self.stage.dynamic(draw, x, y, z=z)
        self.items.append(n)
        return n

    def anchor(self, x: float, y: float) -> Node:
        return self.stage.node(self.kit.dot(2), x, y)

    def link(self, a: Node, b: Node, t: float, **kwargs) -> Link:
        kwargs.setdefault("width", 2)
        line = self.stage.link(a, b, kwargs.pop("color", self.kit.paper), t, **kwargs)
        self.items.append(line)
        return line

    def slide_in(self, n: Node, t: float, dx: float = 80, dur: float = 0.6) -> None:
        x = n.value(t)["x"]
        n.set(t, x=x + dx, opacity=0.0)
        n.animate(n.keys[-1].t, dur, "ease_out_quart", x=x, opacity=1.0)

    def slide_out(self, n: Node, t: float, dx: float = -60, dur: float = 0.4) -> None:
        x = n.value(t)["x"]
        n.animate(max(t, n.keys[-1].t), dur, "ease_in_out", x=x + dx, opacity=0.0)

    def finish(self) -> None:
        """Crossfade out at the end of the scene (the next title is already coming in)."""
        t = self.e - (0.8 if self.last else 0.45)
        for item in self.items:
            if isinstance(item, Link):
                item.t_hide = t if item.t_hide is None else min(item.t_hide, t)
            elif item.value(1e9)["opacity"] > 0:
                item.hide(max(t, item.keys[-1].t), 0.45, dy=0)


# -- common layers --------------------------------------------------------------

def scene_title(ctx: SceneContext) -> None:
    k, sc = ctx.kit, ctx.scene
    if sc.kicker:
        ctx.node(k.label(sc.kicker, 22, k.paper, 6), 540, KICKER_Y).show(ctx.s + 0.1, 0.5, dy=10)
    if sc.title:
        size = k.fit([sc.title], 78, 920)
        ctx.node(k.text(sc.title, size, k.cream), 540, TITLE_Y).show(ctx.s + 0.2, 0.7, rise=True)


def card_times(sc: DocScene) -> list[float]:
    if sc.cards_at is not None:
        return [sc.start + t for t in sc.cards_at]
    first = sc.start + max(2.6, 0.3 * sc.length)
    return [first + i * (sc.card_s + 0.25) for i in range(len(sc.cards))]


def music_cards(ctx: SceneContext) -> None:
    k, sc = ctx.kit, ctx.scene
    for card, t in zip(sc.cards, card_times(sc)):
        n = ctx.node(k.card(card), 540, CARD_Y, z=5)
        ctx.slide_in(n, t)
        if t + sc.card_s < ctx.e - 0.5:
            ctx.slide_out(n, t + sc.card_s)


def fact_box(ctx: SceneContext) -> None:
    k, sc = ctx.kit, ctx.scene
    if not sc.fact:
        return
    if sc.fact_at is not None:
        t = sc.start + sc.fact_at
    else:
        times = card_times(sc)
        t = times[0] + 1.0 if times else sc.start + 2.5
    sprite = k.fact(sc.fact)
    ctx.node(sprite, 540, FACT_Y + sprite.height / 2, z=5).show(t, 0.7, dy=14)


def decade_timeline(stage: Stage, kit: DocKit, doc: Documentary) -> None:
    """Persistent scale 1990–2000 at the top; its marker travels to each scene's year."""
    y0, y1 = doc.timeline
    x0, x1 = 110, 970
    years = y1 - y0
    img = Image.new("RGBA", (x1 - x0 + 80, 70), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    ox = 40
    d.line((ox, 50, ox + x1 - x0, 50), fill=kit.paper, width=2)
    font = kit.fonts.get("mono", 18)
    for i in range(years + 1):
        x = ox + (x1 - x0) * i / years
        major = i in (0, years)
        d.line((x, 44 if not major else 38, x, 50), fill=kit.paper, width=2)
        d.text((x, 26), f"’{str(y0 + i)[-2:]}", font=font, fill=kit.paper if major else kit.olive, anchor="ms")
    scale = stage.node(img, (x0 + x1) / 2, TIMELINE_Y, z=3)
    marker = stage.node(kit.dot(18, kit.cream), x0, TIMELINE_Y + 15, z=4)
    first = doc.scenes[0]
    scale.show(first.start + 0.3, 0.8, dy=0)
    marker.show(first.start + 0.6, 0.5, dy=0, scale_from=0.3)

    def x_of(year: float) -> float:
        return x0 + (x1 - x0) * (year - y0) / years

    for sc in doc.scenes:
        if sc.year is not None:
            marker.animate(max(sc.start + 0.1, marker.keys[-1].t), 0.9, "ease_in_out", x=x_of(sc.year))
    last = doc.scenes[-1]
    scale.hide(last.start + 0.1, 0.6, dy=0)
    marker.hide(last.start + 0.1, 0.6, dy=0)
    marker.pulse = None
