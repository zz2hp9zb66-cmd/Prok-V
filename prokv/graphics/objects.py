"""Editorial objects for music maps: record sleeve, spinning vinyl, city-grid
fragment and small line-art "textures" of instruments. All in palette colours,
no photos (a real cover can be passed to `sleeve` if you have the rights).
"""

from __future__ import annotations

import math

from PIL import Image, ImageDraw, ImageOps

from prokv.graphics.shapes import SS, _canvas, _down
from prokv.style import Palette


def vinyl_record(d: int, p: Palette) -> Image.Image:
    """Vinyl with grooves, a soft sheen and an off-centre label mark so rotation reads."""
    image, draw = _canvas(d, d, SS)
    D = d * SS
    r = D / 2
    draw.ellipse((0, 0, D - 1, D - 1), fill=p.warm_black)
    # Sheen: two opposite pale wedges across the grooves.
    sheen = Image.new("L", (D, D), 0)
    sd = ImageDraw.Draw(sheen)
    for start in (-60, 120):
        sd.pieslice((0, 0, D - 1, D - 1), start, start + 28, fill=34)
    image.paste(Image.new("RGBA", (D, D), p.paper), (0, 0), sheen)
    for k in range(int(r * 0.40), int(r * 0.96), 6 * SS):
        draw.ellipse((r - k, r - k, r + k, r + k), outline=p.espresso, width=SS)
    lr = r * 0.32
    draw.ellipse((r - lr, r - lr, r + lr, r + lr), fill=p.burgundy)
    draw.ellipse((r - lr * 0.86, r - lr * 0.86, r + lr * 0.86, r + lr * 0.86), outline=p.dark_burgundy, width=SS)
    draw.rectangle((r - lr * 0.6, r - lr * 0.55, r + lr * 0.6, r - lr * 0.47), fill=p.cream)  # label text bar
    draw.rectangle((r - lr * 0.35, r + lr * 0.42, r + lr * 0.35, r + lr * 0.48), fill=p.paper)
    hr = r * 0.03
    draw.ellipse((r - hr, r - hr, r + hr, r + hr), fill=p.cream)
    return _down(image, d, d)


def sleeve(size: int, p: Palette, title: str, artist: str, footer: str, fonts,
           cover: Image.Image | None = None) -> Image.Image:
    """A square record sleeve. Typographic by default; or a supplied cover image."""
    image = Image.new("RGBA", (size, size), p.espresso)
    draw = ImageDraw.Draw(image)
    if cover is not None:
        image.paste(ImageOps.fit(cover.convert("RGB"), (size, size), Image.Resampling.LANCZOS), (0, 0))
    else:
        m = int(size * 0.07)
        draw.rectangle((m, m, size - m, size - m), outline=p.olive, width=2)
        title_font = fonts.get("display_italic", int(size * 0.17))
        draw.text((m + 26, m + 26), title, font=title_font, fill=p.cream, anchor="lt")
        small = fonts.get("mono", max(12, int(size * 0.042)))
        draw.text((m + 28, m + 36 + title_font.size), artist.upper(), font=small, fill=p.paper, anchor="lt")
        draw.text((size - m - 24, size - m - 22), footer.upper(), font=small, fill=p.paper, anchor="rb")
        cx, cy, rr = size * 0.5, size * 0.62, size * 0.16
        draw.ellipse((cx - rr, cy - rr, cx + rr, cy + rr), outline=p.burgundy, width=3)
        draw.ellipse((cx - 5, cy - 5, cx + 5, cy + 5), fill=p.burgundy)
    return image


def city_fragment(w: int, h: int, p: Palette, angle: float = 8.0) -> Image.Image:
    """Abstract street grid with a boulevard and a pin — a map fragment, not real data."""
    big = int(max(w, h) * 1.6)
    grid = Image.new("RGBA", (big, big), (0, 0, 0, 0))
    g = ImageDraw.Draw(grid)
    for i in range(0, big, 34):
        g.line((i, 0, i, big), fill=p.olive, width=1)
        g.line((0, i, big, i), fill=p.olive, width=1)
    g.line((0, big * 0.58, big, big * 0.42), fill=p.dark_olive, width=5)   # boulevard
    g.line((big * 0.35, 0, big * 0.55, big), fill=p.paper, width=7)
    grid = grid.rotate(angle, Image.Resampling.BICUBIC)
    image = Image.new("RGBA", (w, h), p.cream)
    image.alpha_composite(grid.crop(((big - w) // 2, (big - h) // 2, (big + w) // 2, (big + h) // 2)))
    d = ImageDraw.Draw(image)
    d.rectangle((0, 0, w - 1, h - 1), outline=p.olive, width=2)
    cx, cy = w * 0.62, h * 0.45
    d.ellipse((cx - 22, cy - 22, cx + 22, cy + 22), outline=p.burgundy, width=3)
    d.ellipse((cx - 8, cy - 8, cx + 8, cy + 8), fill=p.burgundy)
    return image


def instrument(kind: str, size: int, color: str, accent: str) -> Image.Image:
    """Small line-art texture of an instrument."""
    image, d = _canvas(size, size, SS)
    S = size * SS
    w = max(SS, int(S * 0.012))
    kind = kind.lower()
    if kind == "drums":
        r = S * 0.42
        c = S / 2
        d.ellipse((c - r, c - r, c + r, c + r), outline=color, width=w * 2)
        d.ellipse((c - r * 0.25, c - r * 0.25, c + r * 0.25, c + r * 0.25), outline=accent, width=w * 2)
        for k in range(8):
            a = k * math.pi / 4
            x, y = c + math.cos(a) * r * 0.86, c + math.sin(a) * r * 0.86
            d.ellipse((x - w * 2, y - w * 2, x + w * 2, y + w * 2), fill=color)
    elif kind in ("bass", "guitar"):
        strings = 4 if kind == "bass" else 6
        top, bottom = S * 0.22, S * 0.78
        for k in range(strings):
            y = top + (bottom - top) * k / (strings - 1)
            d.line((S * 0.06, y, S * 0.94, y), fill=color, width=w * (3 if kind == "bass" else 1) + (strings - k) // 3)
        for x in (0.28, 0.5, 0.72):
            d.line((S * x, top - S * 0.08, S * x, bottom + S * 0.08), fill=accent, width=w)
        if kind == "guitar":
            d.ellipse((S * 0.59, S * 0.47, S * 0.63, S * 0.53), fill=accent)
    elif kind in ("rhodes", "keys", "piano"):
        keys, top, bottom = 7, S * 0.18, S * 0.82
        kw = S * 0.9 / keys
        for k in range(keys):
            x = S * 0.05 + k * kw
            d.rectangle((x, top, x + kw, bottom), outline=color, width=w * 2)
        for k in (0, 1, 3, 4, 5):
            x = S * 0.05 + (k + 1) * kw - kw * 0.3
            d.rectangle((x, top, x + kw * 0.6, top + (bottom - top) * 0.6), fill=accent if k == 3 else color)
    elif kind == "synth":
        pts = [(S * (0.06 + 0.88 * i / 120), S * 0.36 + math.sin(i / 120 * 4 * math.pi) * S * 0.14)
               for i in range(121)]
        d.line(pts, fill=color, width=w * 2, joint="curve")
        y0, y1 = S * 0.66, S * 0.82
        x = S * 0.06
        step = S * 0.88 / 6
        sq = []
        for k in range(6):
            y = y0 if k % 2 == 0 else y1
            sq += [(x, y), (x + step, y)]
            x += step
        d.line(sq, fill=accent, width=w * 2)
    elif kind in ("lyricon", "wind", "sax"):
        x = S * 0.3
        d.line((x, S * 0.06, x, S * 0.94), fill=color, width=w * 3)
        for k in range(6):
            y = S * (0.16 + k * 0.13)
            d.ellipse((x - S * 0.045, y - S * 0.045, x + S * 0.045, y + S * 0.045), outline=color, width=w * 2)
        for k in range(3):
            pts = [(S * (0.45 + 0.5 * i / 60), S * (0.3 + k * 0.2) + math.sin(i / 60 * 3 * math.pi) * S * 0.04)
                   for i in range(61)]
            d.line(pts, fill=accent, width=w * 2)
    else:
        r = S * 0.3
        d.ellipse((S / 2 - r, S / 2 - r, S / 2 + r, S / 2 + r), outline=color, width=w * 2)
    return _down(image, size, size)


def drum_kit(w: int, h: int, color: str, accent: str) -> Image.Image:
    image, d = _canvas(w, h, SS)
    W, H = w * SS, h * SS
    lw = 3 * SS
    kick_r = W * 0.27
    kx, ky = W * 0.5, H * 0.66
    d.ellipse((kx - kick_r, ky - kick_r, kx + kick_r, ky + kick_r), outline=color, width=lw)
    d.ellipse((kx - kick_r * 0.35, ky - kick_r * 0.35, kx + kick_r * 0.35, ky + kick_r * 0.35), outline=accent, width=lw)
    for tx, tr in ((0.32, 0.12), (0.62, 0.13)):
        cx, cy = W * tx, H * 0.3
        d.ellipse((cx - W * tr, cy - W * tr * 0.7, cx + W * tr, cy + W * tr * 0.7), outline=color, width=lw)
    # hi-hat and cymbal on stands
    for sx, sy, cw in ((0.1, 0.36, 0.13), (0.88, 0.16, 0.16)):
        cx, cy = W * sx, H * sy
        d.line((cx - W * cw, cy, cx + W * cw, cy - W * 0.02), fill=color, width=lw)
        d.line((cx, cy, cx, H * 0.95), fill=color, width=SS * 2)
    d.line((W * 0.07, H * 0.38, W * 0.07 + W * 0.2, H * 0.37), fill=accent, width=lw)
    return _down(image, w, h)


def bass_guitar(w: int, h: int, color: str, accent: str) -> Image.Image:
    """A bass seen front-on, vertical: headstock, neck with frets, body outline."""
    image, d = _canvas(w, h, SS)
    W, H = w * SS, h * SS
    lw = 3 * SS
    cx = W / 2
    nw = W * 0.16
    d.rectangle((cx - nw * 0.7, H * 0.02, cx + nw * 0.7, H * 0.13), outline=color, width=lw)
    for k in range(4):
        y = H * (0.04 + k * 0.025)
        d.ellipse((cx + nw * 0.8, y, cx + nw * 0.8 + W * 0.04, y + W * 0.04), fill=color)
    d.rectangle((cx - nw / 2, H * 0.13, cx + nw / 2, H * 0.62), outline=color, width=lw)
    for k in range(9):
        y = H * (0.16 + k * 0.05)
        d.line((cx - nw / 2, y, cx + nw / 2, y), fill=color, width=SS)
    d.ellipse((cx - W * 0.42, H * 0.55, cx + W * 0.42, H * 0.98), outline=color, width=lw)
    d.rectangle((cx - nw * 0.9, H * 0.82, cx + nw * 0.9, H * 0.86), fill=accent)
    for k in range(4):
        x = cx - nw * 0.36 + k * nw * 0.24
        d.line((x, H * 0.13, x, H * 0.84), fill=accent, width=SS)
    return _down(image, w, h)
