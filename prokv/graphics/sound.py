"""Animated sound graphics: waveforms, a voice line, pitch correction.

All functions return an RGBA sprite for a moment `t`, so they can drive a
DynamicNode. They are schematic illustrations, not measured audio.
"""

from __future__ import annotations

import math

from PIL import Image, ImageDraw

from prokv.graphics.shapes import SS, _canvas, _down


def _noise(i: int, k: int) -> float:
    """Deterministic pseudo-random value in [-1, 1] for bar i at step k."""
    x = math.sin(i * 12.9898 + k * 78.233) * 43758.5453
    return (x - math.floor(x)) * 2 - 1


def bar_wave(w: int, h: int, t: float, roughness: float, color: str, bars: int = 56) -> Image.Image:
    """Audio-style vertical bars. roughness 0 = smooth, polished; 1 = jagged and loud."""
    image, d = _canvas(w, h, SS)
    W, H = w * SS, h * SS
    step = W / bars
    bw = step * 0.55
    k = int(t * 12)                         # the noise pattern changes 12× per second
    frac = t * 12 - k
    for i in range(bars):
        env = math.sin(math.pi * (i + 0.5) / bars) ** 0.8
        smooth = 0.35 + 0.25 * math.sin(i * 0.35 + t * 2.2)
        rough = abs(_noise(i, k) * (1 - frac) + _noise(i, k + 1) * frac)
        amp = env * ((1 - roughness) * smooth + roughness * (0.25 + 0.75 * rough))
        bh = max(SS * 3, amp * H * 0.92)
        x = i * step + (step - bw) / 2
        d.rounded_rectangle((x, (H - bh) / 2, x + bw, (H + bh) / 2), radius=bw / 2, fill=color)
    return _down(image, w, h)


def voice_line(w: int, h: int, t: float, color: str, calm: float = 1.0) -> Image.Image:
    """A soft, slowly breathing line: a sustained human voice."""
    image, d = _canvas(w, h, SS)
    W, H = w * SS, h * SS
    pts = []
    for i in range(241):
        x = i / 240
        env = math.sin(math.pi * x) ** 1.5
        y = (math.sin(x * 14 + t * 1.6 * calm) * 0.6 + math.sin(x * 31 - t * 1.1 * calm) * 0.25
             + math.sin(x * 5 + t * 0.7) * 0.15)
        pts.append((x * W, H / 2 + y * env * H * 0.42))
    d.line(pts, fill=color, width=3 * SS, joint="curve")
    return _down(image, w, h)


def pitch_correction(w: int, h: int, t: float, morph: float, line: str, grid: str,
                     lanes: int = 7) -> Image.Image:
    """A sung pitch contour; with morph → 1 it snaps to note lanes (stepped, Auto-Tune style)."""
    image, d = _canvas(w, h, SS)
    W, H = w * SS, h * SS
    lane_h = H / (lanes + 1)
    if morph > 0.01:  # note lanes fade in with the correction
        alpha = int(255 * min(1.0, morph * 1.4))
        g = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        gd = ImageDraw.Draw(g)
        for n in range(1, lanes + 1):
            gd.line((0, n * lane_h, W, n * lane_h), fill=grid, width=SS)
        g.putalpha(g.getchannel("A").point(lambda v: v * alpha // 255))
        image.alpha_composite(g)
    pts = []
    shift = t * 0.08
    for i in range(301):
        x = i / 300
        natural = (math.sin((x + shift) * 9) * 0.55 + math.sin((x + shift) * 23) * 0.18
                   + math.sin((x + shift) * 53) * 0.07)          # vibrato and slides
        lane = (natural + 1) / 2 * (lanes - 1) + 1
        snapped = round(lane)
        value = lane + (snapped - lane) * morph
        pts.append((x * W, H - value * lane_h))
    d.line(pts, fill=line, width=4 * SS, joint="curve")
    return _down(image, w, h)
