"""Stage -> frames: camera transform, anti-aliased links, nodes, header and progress."""

from __future__ import annotations

import math
from typing import Callable, Iterator

from PIL import Image, ImageDraw

from prokv.animation.stage import Link, Node, Stage
from prokv.graphics.texture import paper

SS = 2  # supersampling for links


class StageRenderer:
    def __init__(self, stage: Stage, fps: int = 30, grain: int = 4,
                 overlay: Callable[[Image.Image, float], None] | None = None) -> None:
        self.stage = stage
        self.fps = fps
        self.background = paper((stage.width, stage.height), stage.background, grain)
        self.overlay = overlay
        self.nodes = sorted(stage.nodes, key=lambda n: n.z)

    @property
    def frame_count(self) -> int:
        return max(1, round(self.stage.duration * self.fps))

    def frames(self) -> Iterator[Image.Image]:
        for i in range(self.frame_count):
            yield self.render(i / self.fps)

    # -- coordinates ---------------------------------------------------------

    def _camera(self, t: float) -> tuple[float, float, float]:
        c = self.stage.camera.value(t)
        return c["cx"], c["cy"], c["zoom"]

    def _to_screen(self, x: float, y: float, cam, fixed: bool = False) -> tuple[float, float]:
        if fixed:
            return x, y
        cx, cy, zoom = cam
        fx, fy = self.stage.focus
        return fx + (x - cx) * zoom, fy + (y - cy) * zoom

    # -- frame ---------------------------------------------------------------

    def render(self, t: float) -> Image.Image:
        frame = self.background.copy()
        cam = self._camera(t)
        for node in (n for n in self.nodes if n.z < 0):
            self._draw_node(frame, node, t, cam)
        self._draw_links(frame, t, cam)
        for node in (n for n in self.nodes if n.z >= 0):
            self._draw_node(frame, node, t, cam)
        if self.overlay:
            self.overlay(frame, t)
        return frame

    def _draw_node(self, frame: Image.Image, node: Node, t: float, cam) -> None:
        v = node.value(t)
        if v["opacity"] <= 0.003:
            return
        zoom = 1.0 if node.fixed else cam[2]
        scale = v["scale"] * zoom * node.pulse_scale(t)
        if scale <= 0.01:
            return
        angle = node.angle(t, v["rot"])
        key = round(scale, 3)
        img = node._cache.get(key)
        if img is None:
            w, h = node.sprite.size
            img = node.sprite if abs(scale - 1) < 1e-3 else node.sprite.resize(
                (max(1, round(w * scale)), max(1, round(h * scale))), Image.Resampling.LANCZOS)
            if len(node._cache) > 64:
                node._cache.clear()
            node._cache[key] = img
        if angle % 360:
            img = img.rotate(angle, Image.Resampling.BICUBIC)
        sx, sy = self._to_screen(v["x"], v["y"], cam, node.fixed)
        x, y = sx - img.width / 2, sy - img.height / 2
        if v["rise"] < 0.999:
            shift = int(round((1 - max(v["rise"], 0)) * img.height))
            if shift >= img.height:
                return
            img = img.crop((0, 0, img.width, img.height - shift))
            y += shift
        alpha = img.getchannel("A")
        if v["opacity"] < 0.997:
            o = v["opacity"]
            alpha = alpha.point(lambda a: int(a * o))
        frame.paste(img, (round(x), round(y)), alpha)

    def _segment(self, link: Link, t: float, cam):
        p = link.progress(t)
        alpha = link.alpha(t)
        if p <= 0 or alpha <= 0.003:
            return None
        va, vb = link.a.value(t), link.b.value(t)
        ax, ay = va["x"] + link.offset_a[0], va["y"] + link.offset_a[1]
        bx, by = vb["x"] + link.offset_b[0], vb["y"] + link.offset_b[1]
        dx, dy = bx - ax, by - ay
        length = math.hypot(dx, dy)
        if length <= link.gap_a + link.gap_b + 1:
            return None
        ux, uy = dx / length, dy / length
        sx, sy = ax + ux * link.gap_a, ay + uy * link.gap_a
        usable = length - link.gap_a - link.gap_b
        ex, ey = sx + ux * usable * p, sy + uy * usable * p
        return self._to_screen(sx, sy, cam), self._to_screen(ex, ey, cam), alpha, p

    def _draw_links(self, frame: Image.Image, t: float, cam) -> None:
        segments = [(link, s) for link in self.stage.links if (s := self._segment(link, t, cam))]
        if not segments:
            return
        pad = 30
        xs = [c for _, s in segments for c in (s[0][0], s[1][0])]
        ys = [c for _, s in segments for c in (s[0][1], s[1][1])]
        x0, y0 = max(0, int(min(xs)) - pad), max(0, int(min(ys)) - pad)
        x1, y1 = min(frame.width, int(max(xs)) + pad), min(frame.height, int(max(ys)) + pad)
        if x1 <= x0 or y1 <= y0:
            return
        layer = Image.new("RGBA", ((x1 - x0) * SS, (y1 - y0) * SS), (0, 0, 0, 0))
        for link, ((ax, ay), (bx, by), alpha, p) in segments:
            # Each link on its own layer so opacity applies per link.
            single = Image.new("RGBA", layer.size, (0, 0, 0, 0))
            d = ImageDraw.Draw(single)
            a = ((ax - x0) * SS, (ay - y0) * SS)
            b = ((bx - x0) * SS, (by - y0) * SS)
            width = max(1, round(link.width * SS))
            if link.dash:
                _dashed(d, a, b, link.dash * SS, link.color, width)
            else:
                d.line([a, b], fill=link.color, width=width)
            if link.arrow and p > 0.85:
                _arrow_head(d, a, b, 14 * SS * min(1, (p - 0.85) / 0.15), link.color, width)
            if alpha < 0.997:
                single.putalpha(single.getchannel("A").point(lambda v: int(v * alpha)))
            layer.alpha_composite(single)
        layer = layer.resize((x1 - x0, y1 - y0), Image.Resampling.LANCZOS)
        frame.paste(layer, (x0, y0), layer)


def _dashed(draw, a, b, dash, color, width) -> None:
    length = math.hypot(b[0] - a[0], b[1] - a[1])
    if length == 0:
        return
    ux, uy = (b[0] - a[0]) / length, (b[1] - a[1]) / length
    pos = 0.0
    while pos < length:
        end = min(pos + dash, length)
        draw.line([(a[0] + ux * pos, a[1] + uy * pos), (a[0] + ux * end, a[1] + uy * end)], fill=color, width=width)
        pos += dash * 2


def _arrow_head(draw, a, b, size, color, width) -> None:
    angle = math.atan2(b[1] - a[1], b[0] - a[0])
    for side in (-1, 1):
        th = angle + math.pi + side * math.radians(30)
        draw.line([b, (b[0] + size * math.cos(th), b[1] + size * math.sin(th))], fill=color, width=width)
