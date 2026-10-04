"""Draws individual video frames from a Project with Pillow.

The renderer only reads the data produced by the earlier stages (composition,
keyframes, captions), so layouts, animation styles and image sources can change
without touching this module. Visual styling lives in LayerStyle / CaptionStyle.
"""

from __future__ import annotations

import bisect
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

from prokv.models import Caption, Keyframe, Layer, Project

EASINGS = {
    "linear": lambda p: p,
    "ease_in": lambda p: p**3,
    "ease_out": lambda p: 1 - (1 - p) ** 3,
    "ease_in_out": lambda p: 4 * p**3 if p < 0.5 else 1 - (-2 * p + 2) ** 3 / 2,
    "hold": lambda p: 0.0,
}

FONT_CANDIDATES = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
    "/Library/Fonts/Arial Bold.ttf",
    "/System/Library/Fonts/Supplemental/Arial Bold.ttf",
    "C:/Windows/Fonts/arialbd.ttf",
]


def interpolate(track: list[Keyframe], t: float) -> Keyframe:
    """Transform of a layer at time t, eased between the surrounding keyframes."""
    if not track:
        return Keyframe(t)
    times = [kf.time_s for kf in track]
    i = bisect.bisect_right(times, t)
    if i == 0:
        return track[0]
    if i == len(track):
        return track[-1]
    a, b = track[i - 1], track[i]
    span = b.time_s - a.time_s
    p = EASINGS.get(a.easing, EASINGS["linear"])((t - a.time_s) / span if span > 0 else 1.0)

    def lerp(x: float, y: float) -> float:
        return x + (y - x) * p

    return Keyframe(
        t,
        offset_x=lerp(a.offset_x, b.offset_x),
        offset_y=lerp(a.offset_y, b.offset_y),
        scale=lerp(a.scale, b.scale),
        rotation=lerp(a.rotation, b.rotation),
        opacity=lerp(a.opacity, b.opacity),
    )


def load_font(size: int, path: str | Path | None = None) -> ImageFont.FreeTypeFont:
    """Load the given font, or the first available bold sans-serif with Cyrillic support."""
    for candidate in [path] if path else FONT_CANDIDATES:
        if candidate and Path(candidate).is_file():
            return ImageFont.truetype(str(candidate), size)
    if path:
        raise FileNotFoundError(f"Font not found: {path}")
    return ImageFont.load_default(size)  # Latin only; pass a font path for other scripts.


@dataclass
class LayerStyle:
    """Editorial "printed photo" look for collage images."""

    border_px: int = 14
    border_color: str = "#FFFFFF"
    shadow_offset: tuple[int, int] = (10, 18)
    shadow_blur: int = 18
    shadow_opacity: float = 0.35


@dataclass
class CaptionStyle:
    font_path: str | None = None
    font_size: int = 68
    text_color: str = "#FFFFFF"
    box_color: tuple[int, int, int, int] = (17, 17, 17, 200)
    padding: tuple[int, int] = (40, 26)  # horizontal, vertical
    corner_radius: int = 24
    line_spacing: int = 12
    max_width_ratio: float = 0.84
    edge_margin: int = 200  # distance from top/bottom edge
    fade_s: float = 0.3


class FrameRenderer:
    """Renders any moment of a Project as an RGB frame."""

    def __init__(
        self,
        project: Project,
        layer_style: LayerStyle | None = None,
        caption_style: CaptionStyle | None = None,
    ) -> None:
        self.project = project
        self.spec = project.spec
        self.layer_style = layer_style or LayerStyle()
        self.caption_style = caption_style or CaptionStyle()
        self.background = Image.new("RGB", (self.spec.width, self.spec.height),
                                    project.composition.background)
        layers = sorted(project.composition.layers, key=lambda layer: layer.z)
        self.tiles = [(layer, self._build_tile(layer)) for layer in layers]
        self.font = load_font(self.caption_style.font_size, self.caption_style.font_path)
        self.captions = [(c, self._build_caption(c.text)) for c in project.captions]

    def render(self, t: float) -> Image.Image:
        frame = self.background.copy()
        for layer, tile in self.tiles:
            kf = interpolate(self.project.animation.tracks.get(layer.id, []), t)
            self._draw_layer(frame, layer, tile, kf)
        for caption, image in self.captions:
            self._draw_caption(frame, caption, image, t)
        return frame

    def _build_tile(self, layer: Layer) -> Image.Image:
        """The layer's image with border and shadow, rotated to its resting angle."""
        style = self.layer_style
        b = style.border_px
        inner = (max(layer.width - 2 * b, 1), max(layer.height - 2 * b, 1))
        with Image.open(layer.image.path) as src:
            photo = ImageOps.fit(src.convert("RGB"), inner, Image.Resampling.LANCZOS)
        framed = Image.new("RGB", (layer.width, layer.height), style.border_color)
        framed.paste(photo, (b, b))

        pad = style.shadow_blur * 2 + max(abs(v) for v in style.shadow_offset)
        size = (layer.width + 2 * pad, layer.height + 2 * pad)
        shadow_alpha = Image.new("L", size, 0)
        ImageDraw.Draw(shadow_alpha).rectangle(
            (pad + style.shadow_offset[0], pad + style.shadow_offset[1],
             pad + style.shadow_offset[0] + layer.width, pad + style.shadow_offset[1] + layer.height),
            fill=int(255 * style.shadow_opacity),
        )
        tile = Image.new("RGBA", size, (0, 0, 0, 0))
        tile.putalpha(shadow_alpha.filter(ImageFilter.GaussianBlur(style.shadow_blur)))
        tile.paste(framed, (pad, pad))
        # PIL rotates counter-clockwise; layer.rotation is clockwise degrees.
        return tile.rotate(-layer.rotation, Image.Resampling.BICUBIC, expand=True)

    def _draw_layer(self, frame: Image.Image, layer: Layer, tile: Image.Image, kf: Keyframe) -> None:
        if kf.opacity <= 0.01 or kf.scale <= 0:
            return
        if kf.rotation:
            tile = tile.rotate(-kf.rotation, Image.Resampling.BICUBIC, expand=True)
        if abs(kf.scale - 1.0) > 1e-3:
            size = (max(round(tile.width * kf.scale), 1), max(round(tile.height * kf.scale), 1))
            tile = tile.resize(size, Image.Resampling.BILINEAR)
        cx = layer.x + layer.width / 2 + kf.offset_x
        cy = layer.y + layer.height / 2 + kf.offset_y
        frame.paste(tile, (round(cx - tile.width / 2), round(cy - tile.height / 2)),
                    _fade_mask(tile, kf.opacity))

    def _build_caption(self, text: str) -> Image.Image:
        style = self.caption_style
        max_text_w = self.spec.width * style.max_width_ratio - 2 * style.padding[0]
        lines = _wrap(text, self.font, max_text_w)
        ascent, descent = self.font.getmetrics()
        line_h = ascent + descent
        text_w = max(self.font.getlength(line) for line in lines)
        text_h = line_h * len(lines) + style.line_spacing * (len(lines) - 1)
        w, h = int(text_w + 2 * style.padding[0]), int(text_h + 2 * style.padding[1])

        box = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        draw = ImageDraw.Draw(box)
        draw.rounded_rectangle((0, 0, w - 1, h - 1), style.corner_radius, fill=style.box_color)
        y = style.padding[1]
        for line in lines:
            draw.text(((w - self.font.getlength(line)) / 2, y), line, font=self.font,
                      fill=style.text_color)
            y += line_h + style.line_spacing
        return box

    def _draw_caption(self, frame: Image.Image, caption: Caption, image: Image.Image, t: float) -> None:
        if not caption.start_s <= t < caption.end_s:
            return
        fade = self.caption_style.fade_s
        opacity = min(1.0, (t - caption.start_s) / fade, (caption.end_s - t) / fade) if fade > 0 else 1.0
        if opacity <= 0.01:
            return
        margin = self.caption_style.edge_margin
        y = {
            "top": margin,
            "center": (self.spec.height - image.height) // 2,
        }.get(caption.position, self.spec.height - margin - image.height)
        x = (self.spec.width - image.width) // 2
        frame.paste(image, (x, y), _fade_mask(image, opacity))


def _fade_mask(image: Image.Image, opacity: float) -> Image.Image:
    alpha = image.getchannel("A")
    if opacity >= 0.999:
        return alpha
    return alpha.point(lambda v: int(v * opacity))


def _wrap(text: str, font: ImageFont.FreeTypeFont, max_width: float) -> list[str]:
    """Greedy word wrap; explicit newlines in the caption are kept."""
    lines = []
    for paragraph in text.splitlines() or [""]:
        current = ""
        for word in paragraph.split():
            candidate = f"{current} {word}".strip()
            if current and font.getlength(candidate) > max_width:
                lines.append(current)
                current = word
            else:
                current = candidate
        lines.append(current)
    return lines
