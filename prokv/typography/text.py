"""Text layout: word wrapping, auto-fitting, highlighted words, per-word sprites.

Headlines are laid out word by word so each word can be animated on its own
(kinetic typography) while sharing one baseline grid.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from PIL import Image, ImageDraw, ImageFont


@dataclass
class PlacedWord:
    text: str
    x: float            # left edge, relative to the layout box
    baseline: float     # baseline y, relative to the layout box
    width: float
    highlight: bool
    line: int


@dataclass
class TextLayout:
    words: list[PlacedWord] = field(default_factory=list)
    width: float = 0
    height: float = 0
    font: ImageFont.FreeTypeFont | None = None
    accent_font: ImageFont.FreeTypeFont | None = None
    line_height: float = 0
    lines: int = 0


def _norm(word: str) -> str:
    return re.sub(r"[^\w-]", "", word.lower())


def layout_text(
    text: str,
    font: ImageFont.FreeTypeFont,
    max_width: float,
    leading: float = 1.1,
    highlights: list[str] | None = None,
    accent_font: ImageFont.FreeTypeFont | None = None,
    align: str = "left",
) -> TextLayout:
    """Greedy word wrap. Words in `highlights` use `accent_font` (e.g. italic)."""
    accent_font = accent_font or font
    marked = {_norm(w) for h in (highlights or []) for w in h.split()}
    space = font.getlength(" ")
    ascent, descent = font.getmetrics()
    line_h = (ascent + descent) * leading

    lines: list[list[tuple[str, float, bool]]] = [[]]
    line_w = 0.0
    for raw in text.split():
        hl = _norm(raw) in marked
        w = (accent_font if hl else font).getlength(raw)
        needed = w if not lines[-1] else line_w + space + w
        if lines[-1] and needed > max_width:
            lines.append([])
            line_w = 0.0
            needed = w
        lines[-1].append((raw, w, hl))
        line_w = needed

    layout = TextLayout(font=font, accent_font=accent_font, line_height=line_h, lines=len(lines))
    for li, line in enumerate(lines):
        total = sum(w for _, w, _ in line) + space * (len(line) - 1)
        x = {"center": (max_width - total) / 2, "right": max_width - total}.get(align, 0.0)
        baseline = ascent + li * line_h
        for word, w, hl in line:
            layout.words.append(PlacedWord(word, x, baseline, w, hl, li))
            x += w + space
        layout.width = max(layout.width, total)
    layout.height = ascent + descent + (len(lines) - 1) * line_h
    return layout


def fit_layout(text, font_for_size, max_width, max_height, size, min_size, max_lines=6, **kwargs) -> TextLayout:
    """Largest size (stepping down from `size`) whose layout fits the box.

    `font_for_size(size)` returns (font, accent_font).
    """
    current = size
    while True:
        font, accent = font_for_size(current)
        layout = layout_text(text, font, max_width, accent_font=accent, **kwargs)
        too_wide = any(w.width > max_width for w in layout.words)
        if (layout.height <= max_height and layout.lines <= max_lines and not too_wide) or current <= min_size:
            return layout
        current = max(min_size, int(current * 0.93))


def word_sprite(word: PlacedWord, layout: TextLayout, color: str, accent_color: str | None = None) -> tuple[Image.Image, int]:
    """RGBA image of one word plus the y offset of its top edge above the baseline."""
    font = layout.accent_font if word.highlight else layout.font
    ascent, descent = font.getmetrics()
    pad = int(ascent * 0.08) + 2
    w = int(word.width + 2 * pad)
    h = ascent + descent + 2 * pad
    image = Image.new("RGBA", (max(w, 1), h), (0, 0, 0, 0))
    ImageDraw.Draw(image).text((pad, pad + ascent), word.text, font=font, anchor="ls",
                               fill=(accent_color or color) if word.highlight else color)
    return image, pad + ascent


def label_sprite(text: str, font: ImageFont.FreeTypeFont, color: str, tracking: int = 0) -> Image.Image:
    """Small uppercase label with letter-spacing (kickers, indices, header)."""
    text = text.upper()
    ascent, descent = font.getmetrics()
    widths = [font.getlength(ch) for ch in text]
    total = int(sum(widths) + tracking * max(len(text) - 1, 0)) + 4
    image = Image.new("RGBA", (max(total, 1), ascent + descent + 4), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    x = 2.0
    for ch, w in zip(text, widths):
        draw.text((x, 2 + ascent), ch, font=font, anchor="ls", fill=color)
        x += w + tracking
    return image


def text_sprite(text: str, font: ImageFont.FreeTypeFont, color: str) -> Image.Image:
    ascent, descent = font.getmetrics()
    w = int(font.getlength(text)) + 8
    image = Image.new("RGBA", (max(w, 1), ascent + descent + 8), (0, 0, 0, 0))
    ImageDraw.Draw(image).text((4, 4 + ascent), text, font=font, anchor="ls", fill=color)
    return image
