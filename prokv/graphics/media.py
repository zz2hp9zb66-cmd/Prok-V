"""Schematic objects for music documentaries: a dot-matrix map of Europe and
sound-carrier icons (cassette, CD, MP3 file). Line art in palette colours.
"""

from __future__ import annotations

from PIL import Image, ImageDraw

from prokv.graphics.shapes import SS, _canvas, _down

# A deliberately rough outline (normalised 0..1, x → east, y → south). Not geography-accurate.
_EUROPE = [
    [(0.05, 0.80), (0.05, 0.66), (0.13, 0.61), (0.23, 0.62), (0.21, 0.53), (0.28, 0.48), (0.34, 0.44),
     (0.41, 0.40), (0.47, 0.37), (0.52, 0.40), (0.62, 0.36), (0.74, 0.32), (0.88, 0.30), (0.96, 0.36),
     (0.96, 0.68), (0.86, 0.70), (0.78, 0.78), (0.70, 0.76), (0.67, 0.86), (0.62, 0.80), (0.58, 0.70),
     (0.55, 0.66), (0.60, 0.80), (0.60, 0.92), (0.55, 0.88), (0.50, 0.72), (0.46, 0.64), (0.40, 0.66),
     (0.33, 0.64), (0.28, 0.72), (0.22, 0.82), (0.12, 0.86)],
    [(0.22, 0.44), (0.20, 0.34), (0.24, 0.22), (0.29, 0.24), (0.30, 0.36), (0.32, 0.44)],          # Britain
    [(0.13, 0.36), (0.14, 0.28), (0.19, 0.29), (0.18, 0.38)],                                      # Ireland
    [(0.47, 0.30), (0.50, 0.12), (0.60, 0.03), (0.72, 0.06), (0.70, 0.18), (0.64, 0.27), (0.56, 0.30)],
]
# Unlabelled "music centres" for the pulsing links (roughly London, Benelux, Paris, Rhine, Berlin, Milan).
EUROPE_CENTRES = [(0.27, 0.38), (0.39, 0.42), (0.32, 0.53), (0.45, 0.50), (0.53, 0.42), (0.47, 0.62)]


def europe_dots(w: int, h: int, color: str, spacing: int = 16, dot: int = 5) -> Image.Image:
    mask = Image.new("L", (w, h), 0)
    md = ImageDraw.Draw(mask)
    for poly in _EUROPE:
        md.polygon([(x * w, y * h) for x, y in poly], fill=255)
    image, d = _canvas(w, h, SS)
    for y in range(spacing // 2, h, spacing):
        for x in range(spacing // 2, w, spacing):
            if mask.getpixel((x, y)):
                r = dot / 2 * SS
                d.ellipse((x * SS - r, y * SS - r, x * SS + r, y * SS + r), fill=color)
    return _down(image, w, h)


def cassette(w: int, color: str, accent: str) -> Image.Image:
    h = int(w * 0.64)
    image, d = _canvas(w, h, SS)
    W, H, lw = w * SS, h * SS, 3 * SS
    d.rounded_rectangle((lw, lw, W - lw, H - lw), radius=H * 0.08, outline=color, width=lw)
    d.rounded_rectangle((W * 0.18, H * 0.22, W * 0.82, H * 0.58), radius=H * 0.06, outline=color, width=lw)
    for cx in (W * 0.34, W * 0.66):
        r = H * 0.11
        d.ellipse((cx - r, H * 0.40 - r, cx + r, H * 0.40 + r), outline=accent, width=lw)
    d.polygon([(W * 0.25, H - lw), (W * 0.32, H * 0.74), (W * 0.68, H * 0.74), (W * 0.75, H - lw)],
              outline=color, width=lw)
    return _down(image, w, h)


def compact_disc(d_px: int, color: str, accent: str) -> Image.Image:
    image, d = _canvas(d_px, d_px, SS)
    D, lw = d_px * SS, 3 * SS
    d.ellipse((lw, lw, D - lw, D - lw), outline=color, width=lw)
    d.arc((D * 0.14, D * 0.14, D * 0.86, D * 0.86), 200, 290, fill=accent, width=lw * 2)
    r = D * 0.16
    d.ellipse((D / 2 - r, D / 2 - r, D / 2 + r, D / 2 + r), outline=color, width=lw)
    r = D * 0.05
    d.ellipse((D / 2 - r, D / 2 - r, D / 2 + r, D / 2 + r), fill=color)
    return _down(image, d_px, d_px)


def mp3_file(w: int, color: str, accent: str, font) -> Image.Image:
    h = int(w * 1.25)
    image, d = _canvas(w, h, SS)
    W, H, lw = w * SS, h * SS, 3 * SS
    fold = W * 0.28
    d.line([(lw, lw), (W - fold, lw), (W - lw, fold), (W - lw, H - lw), (lw, H - lw), (lw, lw)],
           fill=color, width=lw, joint="curve")
    d.line([(W - fold, lw), (W - fold, fold), (W - lw, fold)], fill=color, width=lw)
    image = _down(image, w, h)
    ImageDraw.Draw(image).text((w / 2, h * 0.62), "MP3", font=font, fill=accent, anchor="mm")
    return image
