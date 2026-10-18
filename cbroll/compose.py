"""Scene layout: plan + template -> concrete layers in scene.json.

A template is a table of named slots (position, size, rotation, depth). The
scene plan maps subjects to slots; compose fills them, adds headline / caption /
name labels and a small seeded jitter so re-composing with another seed gives
a different but still balanced arrangement. Manual tweaks are made later in
scene.json itself (or by asking Claude Code), compose only builds the first draft.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

import cv2
import numpy as np
from PIL import Image

from .cutout import _noise_field
from .project import ProjectDir
from .schemas import Layer, Scene

W, H = 1080, 1920


@dataclass
class Slot:
    x: float
    y: float
    w: float
    rot: float
    z: int
    depth: float
    h: float | None = None


@dataclass
class TextSlot:
    x: float
    y: float
    size: int
    rot: float
    z: int
    depth: float
    style: str  # headline, caption, label, stamp


@dataclass
class Template:
    paper: str
    slots: dict[str, Slot]
    texts: dict[str, TextSlot]
    blocks: list[tuple[Slot, str]]  # torn colour blocks: slot, palette colour
    label_offset: tuple[float, float] = (0, 0.42)  # relative to subject size


TEMPLATES: dict[str, Template] = {
    # Two portraits in front of a city / place photo.
    "duo": Template(
        paper="cream",
        slots={
            "bg_photo": Slot(540, 800, 980, -2, 1, 0.15),
            "prop1": Slot(720, 600, 540, -5, 3, 0.5),
            "hero1": Slot(330, 1310, 600, -3, 5, 0.75),
            "hero2": Slot(770, 1350, 600, 3, 6, 0.8),
        },
        texts={
            "headline": TextSlot(320, 380, 300, -5, 8, 0.95, "headline"),
            "caption": TextSlot(770, 270, 40, 3, 9, 0.9, "label"),
        },
        blocks=[(Slot(540, 1500, 1200, 3, 2, 0.3, h=600), "blue")],
        label_offset=(0, 0.36),
    ),
    # One performer with a couple of props.
    "hero_props": Template(
        paper="kraft",
        slots={
            "bg_photo": Slot(540, 880, 1000, 2, 1, 0.15),
            "prop1": Slot(860, 900, 300, 8, 4, 0.55),
            "hero1": Slot(460, 1170, 600, -1, 5, 0.7),
            "prop2": Slot(380, 1560, 640, -10, 6, 0.85),
        },
        texts={
            "headline": TextSlot(470, 300, 190, -3, 8, 0.95, "headline"),
            "caption": TextSlot(700, 1770, 40, -2, 9, 0.9, "caption"),
        },
        blocks=[(Slot(540, 1440, 1240, -7, 2, 0.3, h=320), "accent")],
    ),
    # Overlapping objects piled up like a desk collage.
    "stack": Template(
        paper="cream",
        slots={
            "bg_photo": Slot(540, 760, 920, -3, 1, 0.15),
            "prop3": Slot(360, 1230, 560, -8, 2, 0.4),
            "prop2": Slot(740, 1210, 540, 6, 3, 0.45),
            "prop1": Slot(870, 680, 280, 7, 4, 0.6),
            "hero1": Slot(540, 1600, 780, -2, 5, 0.75),
        },
        texts={
            "headline": TextSlot(300, 300, 230, -4, 8, 0.95, "headline"),
            "caption": TextSlot(560, 470, 38, 2, 9, 0.9, "label"),
        },
        blocks=[(Slot(820, 330, 560, 4, 0, 0.1, h=300), "blue")],
    ),
    # Typographic poster with two performers.
    "poster": Template(
        paper="blue",
        slots={
            "hero1": Slot(330, 1250, 540, -2, 5, 0.75),
            "hero2": Slot(780, 1300, 640, 3, 6, 0.8),
            "prop1": Slot(850, 560, 320, 14, 7, 0.9),
            "prop2": Slot(250, 1700, 420, -6, 7, 0.85),
        },
        texts={
            "headline": TextSlot(380, 500, 300, -4, 3, 0.4, "poster"),
            "caption": TextSlot(680, 1800, 60, -3, 9, 0.95, "stamp"),
        },
        blocks=[(Slot(540, 1180, 1040, -3, 1, 0.25, h=880), "cream")],
        label_offset=(0, 0.3),
    ),
}

PAPERS = {"cream": "#efe6d2", "kraft": "#c8a777", "blue": "#1d3f8f", "dark": "#1b1b1b"}


def paper_background(pd: ProjectDir, name: str, seed: int) -> str:
    """Full-frame paper sheet with fibres, creases and a soft vignette."""
    path = pd.abs(f"assets/backgrounds/paper_{name}.jpg")
    if path.exists():
        return pd.rel(path)
    rng = np.random.default_rng(seed)
    base = np.array(Image.new("RGB", (1, 1), PAPERS[name]).getpixel((0, 0)), np.float32) / 255
    img = np.ones((H, W, 3), np.float32) * base
    tone = (_noise_field(H, W, rng, 300) - 0.5) * 0.08 + (_noise_field(H, W, rng, 30) - 0.5) * 0.04
    fibre = (_noise_field(H, W, rng, 2) - 0.5) * 0.06
    img += (tone + fibre)[..., None]
    for _ in range(2):  # creases
        y = rng.integers(300, H - 300)
        crease = np.exp(-((np.arange(H) - y) ** 2) / 30.0)[:, None] * 0.06
        img[..., :] += crease[..., None] - np.roll(crease, 3, axis=0)[..., None]
    yy, xx = np.mgrid[0:H, 0:W]
    r = np.sqrt(((xx - W / 2) / W) ** 2 + ((yy - H / 2) / H) ** 2)
    img *= (1 - 0.3 * np.clip(r - 0.3, 0, 1))[..., None]
    Image.fromarray((np.clip(img, 0, 1) * 255).astype(np.uint8)).save(path, quality=90)
    return pd.rel(path)


def grain_overlay(pd: ProjectDir) -> str:
    path = pd.abs("assets/textures/grain.png")
    if not path.exists():
        rng = np.random.default_rng(0)
        g = rng.normal(128, 38, (H // 2, W // 2)).clip(0, 255).astype(np.uint8)
        g = cv2.resize(g, (W, H), interpolation=cv2.INTER_NEAREST)
        Image.fromarray(g).save(path)
    return pd.rel(path)


def _asset_size(pd: ProjectDir, rel: str) -> tuple[int, int]:
    with Image.open(pd.abs(rel)) as im:
        return im.size


def compose_scene(pd: ProjectDir, scene: Scene) -> Scene:
    tpl = TEMPLATES[scene.template or "duo"]
    rnd = random.Random(scene.seed)
    jitter = lambda v: v + rnd.uniform(-1, 1)  # noqa: E731
    palette = pd.project().palette
    layers: list[Layer] = []

    scene.background = paper_background(pd, tpl.paper, seed=len(tpl.paper))

    for i, (slot, colour) in enumerate(tpl.blocks):
        layers.append(
            Layer(
                id=f"block{i + 1}", kind="shape", shape="torn_rect", bg=palette.get(colour, PAPERS.get(colour)),
                x=jitter(slot.x), y=jitter(slot.y), w=slot.w, h=slot.h, rotation=slot.rot + rnd.uniform(-1, 1),
                z=slot.z, depth=slot.depth, shadow=False,
            )
        )

    for subject in scene.plan.subjects:
        slot = tpl.slots.get(subject.slot)
        if slot is None or subject.asset is None:
            continue
        meta = pd.meta(subject.asset)
        rel = meta.styled or meta.original
        aw, ah = _asset_size(pd, rel)
        layer = Layer(
            id=subject.slot, kind="cutout" if meta.cut else "photo", asset=rel,
            x=slot.x + rnd.uniform(-12, 12), y=slot.y + rnd.uniform(-12, 12), w=slot.w,
            rotation=slot.rot + rnd.uniform(-1.5, 1.5), z=slot.z, depth=slot.depth,
            tape=not meta.cut and rnd.random() < 0.7,
        )
        layers.append(layer)
        if subject.label:
            h = slot.w * ah / aw
            dx, dy = tpl.label_offset
            layers.append(
                Layer(
                    id=f"{subject.slot}_label", kind="text", text=subject.label, font="label", font_size=34,
                    color=palette["ink"], bg=palette["cream"], x=layer.x + dx * slot.w, y=layer.y + dy * h,
                    w=0, rotation=rnd.uniform(-4, 4), z=20 + slot.z, depth=min(1.0, slot.depth + 0.1),
                )
            )

    texts = {"headline": scene.plan.headline, "caption": scene.plan.caption}
    for key, text in texts.items():
        ts = tpl.texts.get(key)
        if not text or ts is None:
            continue
        on_dark = tpl.paper in ("blue", "dark")
        style = {
            "headline": dict(font="headline", color=palette["accent"], bg=None),
            "poster": dict(font="poster", color=palette["cream"], bg=None),
            "label": dict(font="label", color=palette["ink"], bg=palette["cream"]),
            "caption": dict(font="caption", color=palette["cream"], bg=palette["ink"]),
            "stamp": dict(font="stamp", color=palette["accent"] if not on_dark else palette["cream"], bg=None),
        }[ts.style]
        layers.append(
            Layer(
                id=key, kind="text", text=text, font_size=ts.size, x=ts.x, y=ts.y, w=0,
                rotation=ts.rot, z=ts.z, depth=ts.depth, shadow=ts.style in ("label", "caption"), **style,
            )
        )

    layers.append(Layer(id="grain", kind="texture", asset=grain_overlay(pd), z=100, depth=0.5, opacity=0.12,
                        blend="overlay", shadow=False, x=W / 2, y=H / 2, w=W))
    scene.layers = sorted(layers, key=lambda l: l.z)
    return scene
