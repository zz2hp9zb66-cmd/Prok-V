"""A window onto a source image: animated crop (Ken Burns / detail moves) and mask
reveal. The source is never changed — every frame is a fresh crop + resize of it.

Boxes are normalised (x0, y0, x1, y1) in source coordinates; each box is expanded
to the window's aspect ratio around its centre and clamped inside the image, so
nothing outside the original picture is ever shown or invented.
"""

from __future__ import annotations

from dataclasses import dataclass

from PIL import Image

from prokv.animation.easing import ease

FULL = (0.0, 0.0, 1.0, 1.0)


def fit_box(box, src_size: tuple[int, int], aspect: float) -> tuple[float, float, float, float]:
    """Pixel crop box with the window's aspect ratio, containing `box` where possible."""
    sw, sh = src_size
    x0, y0, x1, y1 = box[0] * sw, box[1] * sh, box[2] * sw, box[3] * sh
    w, h = x1 - x0, y1 - y0
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    if w / h > aspect:
        h = w / aspect
    else:
        w = h * aspect
    if w > sw:
        w, h = sw, sw / aspect
    if h > sh:
        h, w = sh, sh * aspect
    cx = min(max(cx, w / 2), sw - w / 2)
    cy = min(max(cy, h / 2), sh - h / 2)
    return cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2


@dataclass
class Move:
    t: float
    box: tuple[float, float, float, float]
    easing: str = "ease_in_out_sine"


class ImageView:
    """draw(t) → RGB(A) frame of size (w, h). Use as a DynamicNode's draw function."""

    def __init__(self, src: Image.Image, w: int, h: int, moves: list[Move] | None = None,
                 reveal: tuple[float, float, str] | None = None) -> None:
        self.src, self.w, self.h = src, w, h
        self.moves = moves or [Move(0.0, FULL)]
        self.reveal = reveal              # (t0, t1, "left"|"up"|"down") mask reveal
        self.aspect = w / h
        self._last = None

    def box_at(self, t: float):
        m = self.moves
        if t <= m[0].t:
            return fit_box(m[0].box, self.src.size, self.aspect)
        for a, b in zip(m, m[1:]):
            if a.t <= t <= b.t:
                p = ease(b.easing, (t - a.t) / (b.t - a.t)) if b.t > a.t else 1.0
                ba, bb = fit_box(a.box, self.src.size, self.aspect), fit_box(b.box, self.src.size, self.aspect)
                return tuple(u + (v - u) * p for u, v in zip(ba, bb))
        return fit_box(m[-1].box, self.src.size, self.aspect)

    def __call__(self, t: float) -> Image.Image:
        box = tuple(round(v, 1) for v in self.box_at(t))
        if self._last and self._last[0] == box:
            frame = self._last[1]
        else:
            frame = self.src.resize((self.w, self.h), Image.Resampling.BICUBIC, box=box).convert("RGBA")
            self._last = (box, frame)
        if self.reveal:
            t0, t1, direction = self.reveal
            p = ease("ease_in_out", (t - t0) / (t1 - t0)) if t1 > t0 else 1.0
            if p < 1.0:
                out = Image.new("RGBA", frame.size, (0, 0, 0, 0))
                if direction == "up":
                    cut = int(self.h * (1 - p))
                    out.paste(frame.crop((0, cut, self.w, self.h)), (0, cut))
                elif direction == "down":
                    out.paste(frame.crop((0, 0, self.w, max(1, int(self.h * p)))), (0, 0))
                else:
                    out.paste(frame.crop((0, 0, max(1, int(self.w * p)), self.h)), (0, 0))
                return out
        return frame
