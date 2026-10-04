"""Visual style: palette and every colour/typography setting used to draw a video.

All look-and-feel decisions live here, separate from rendering logic. To change
the look, edit WARM_STRICT or pass another VisualStyle to Pipeline(style=...).

Direction: WARM × STRICT — warm, restrained, calm, adult, editorial. A mix of
editorial magazine, archival music photography, vinyl culture and a modern wine
bar; understated. Cream/beige is the light contrast, burgundy the main accent,
olive the calm secondary accent. No pure RGB colours, neon, cold blues or bright
purples; tints and shades of the palette only.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Palette:
    burgundy: str = "#5A171B"       # deep wine
    dark_burgundy: str = "#351315"
    cream: str = "#E8DDC8"          # warm cream
    paper: str = "#CBB99A"          # paper beige
    dark_olive: str = "#303126"
    olive: str = "#535342"          # muted olive
    espresso: str = "#2B201A"
    warm_black: str = "#171512"

    def colors(self) -> list[str]:
        return list(self.__dict__.values())


@dataclass(frozen=True)
class PlaceholderStyle:
    """Look of the offline stand-in images: palette gradient + one motif + grain.

    Motifs: vinyl record, arch, horizontal band with a rule. Burgundy dominates,
    olive is secondary, cream/paper give the light contrast.
    """

    # (gradient top, gradient bottom, motif colour); picked per image from the prompt.
    schemes: tuple[tuple[str, str, str], ...] = (
        ("#5A171B", "#351315", "#CBB99A"),  # burgundy / paper
        ("#CBB99A", "#E8DDC8", "#5A171B"),  # paper / burgundy
        ("#535342", "#303126", "#E8DDC8"),  # olive / cream
        ("#351315", "#2B201A", "#5A171B"),  # dark burgundy / burgundy
        ("#E8DDC8", "#CBB99A", "#303126"),  # cream / dark olive
        ("#2B201A", "#171512", "#CBB99A"),  # espresso / paper
    )
    record_color: str = "#171512"   # vinyl disc; its label uses the scheme's motif colour
    grain: int = 10                 # grain std-dev, 0 to disable


@dataclass(frozen=True)
class LayerStyle:
    """Collage images as archival prints: warm toning, thin light border, soft warm shadow."""

    tone_dark: str = "#2B201A"      # duotone applied to every image so real photos
    tone_light: str = "#E8DDC8"     # sit in the palette too (archival print look)
    tone_strength: float = 0.35     # 0 = original colours, 1 = full duotone
    border_px: int = 12
    border_color: str = "#F3ECDF"   # a lighter tint of cream so it reads on the cream background
    shadow_color: str = "#171512"
    shadow_offset: tuple[int, int] = (8, 16)
    shadow_blur: int = 20
    shadow_opacity: float = 0.28


SERIF_BOLD_FONTS = (
    "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
    "/usr/share/fonts/truetype/freefont/FreeSerifBold.ttf",
    "/System/Library/Fonts/Supplemental/Times New Roman Bold.ttf",
    "/Library/Fonts/Times New Roman Bold.ttf",
    "C:/Windows/Fonts/timesbd.ttf",
)


@dataclass(frozen=True)
class CaptionStyle:
    """Editorial captions: serif text in a flat, square-cornered block."""

    font_path: str | None = None    # explicit font; otherwise the first of font_candidates found
    font_candidates: tuple[str, ...] = SERIF_BOLD_FONTS
    font_size: int = 70
    text_color: str = "#E8DDC8"
    box_color: str = "#5A171B"
    box_opacity: float = 0.94
    padding: tuple[int, int] = (44, 30)  # horizontal, vertical
    corner_radius: int = 2
    line_spacing: int = 10
    max_width_ratio: float = 0.82
    edge_margin: int = 210          # distance from top/bottom edge
    fade_s: float = 0.35


@dataclass(frozen=True)
class VisualStyle:
    name: str
    palette: Palette = field(default_factory=Palette)
    background: str = "#E8DDC8"
    background_grain: int = 5       # subtle paper texture, 0 to disable
    rule_color: str = "#535342"     # thin olive editorial rules near the top and bottom
    rule_inset: tuple[int, int] = (60, 96)  # horizontal, vertical distance from the edges
    rule_px: int = 2
    placeholder: PlaceholderStyle = field(default_factory=PlaceholderStyle)
    layer: LayerStyle = field(default_factory=LayerStyle)
    caption: CaptionStyle = field(default_factory=CaptionStyle)


WARM_STRICT = VisualStyle(name="warm_strict")
DEFAULT_STYLE = WARM_STRICT


def hex_to_rgb(color: str) -> tuple[int, int, int]:
    color = color.lstrip("#")
    return tuple(int(color[i:i + 2], 16) for i in (0, 2, 4))
