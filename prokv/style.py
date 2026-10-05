"""Visual system: every colour, font, size, spacing, timing and scene-theme setting.

Nothing visual is hard-coded elsewhere — templates and the renderer read from a
VisualStyle. Change the look by editing WARM_STRICT here, or without touching code
by passing a JSON override file (`--style my_style.json`, see examples/).

Direction: WARM × STRICT — warm, strict, intellectual, calm, adult, editorial,
minimal; vinyl, music, culture, restaurants, wine bars, modern spaces. Cream/beige
is the light contrast, burgundy the main accent, olive the calm secondary accent.
No colours outside the palette: no neon, bright blue, purple or pure RGB.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, fields, is_dataclass, replace
from pathlib import Path


@dataclass(frozen=True)
class Palette:
    burgundy: str = "#5A171B"
    dark_burgundy: str = "#351315"
    cream: str = "#E8DDC8"
    paper: str = "#CBB99A"
    dark_olive: str = "#303126"
    olive: str = "#535342"
    espresso: str = "#2B201A"
    warm_black: str = "#171512"

    def colors(self) -> list[str]:
        return [getattr(self, f.name) for f in fields(self)]


_P = Palette()


@dataclass(frozen=True)
class Fonts:
    """Font roles. Each is a list of candidate files; the first one installed is used.

    All defaults support Cyrillic. To use your own font, put its path first.
    """

    display: tuple[str, ...] = (       # headlines, numbers: serif bold
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",
        "/System/Library/Fonts/Supplemental/Times New Roman Bold.ttf",
        "C:/Windows/Fonts/timesbd.ttf",
    )
    display_italic: tuple[str, ...] = (  # highlighted words, quotes
        "/usr/share/fonts/truetype/liberation/LiberationSerif-BoldItalic.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSerifBoldItalic.ttf",
        "/System/Library/Fonts/Supplemental/Times New Roman Bold Italic.ttf",
        "C:/Windows/Fonts/timesbi.ttf",
    )
    serif: tuple[str, ...] = (         # secondary serif text
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
        "/System/Library/Fonts/Supplemental/Times New Roman.ttf",
        "C:/Windows/Fonts/times.ttf",
    )
    serif_italic: tuple[str, ...] = (
        "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSerifItalic.ttf",
        "/System/Library/Fonts/Supplemental/Times New Roman Italic.ttf",
        "C:/Windows/Fonts/timesi.ttf",
    )
    text: tuple[str, ...] = (          # body copy: sans
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "C:/Windows/Fonts/arial.ttf",
    )
    mono: tuple[str, ...] = (          # labels, indices, counters
        "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "/System/Library/Fonts/Supplemental/Courier New.ttf",
        "C:/Windows/Fonts/cour.ttf",
    )


@dataclass(frozen=True)
class TypeScale:
    """Font sizes in px (at 1080 wide). Templates shrink text to fit when needed."""

    hero: int = 250          # big numbers
    display: int = 116       # main statement
    title: int = 82          # scene headlines
    subtitle: int = 58       # list items, comparison sides
    body: int = 40           # secondary text
    label: int = 26          # kickers, indices, header
    display_leading: float = 1.06
    body_leading: float = 1.38
    label_tracking: int = 5  # extra px between letters in labels
    min_scale: float = 0.5   # smallest auto-fit size relative to the nominal size


@dataclass(frozen=True)
class Spacing:
    margin_x: int = 96
    safe_top: int = 300      # content starts below this (header + Reels UI)
    safe_bottom: int = 430   # content ends above height - this (Reels caption/UI)
    header_y: int = 150
    footer_y: int = 1800
    gap: int = 44            # default vertical gap between blocks
    rule_px: int = 3         # weight of accent rules
    hairline_px: int = 2     # weight of thin lines, frames


@dataclass(frozen=True)
class MotionConfig:
    speed: float = 1.0           # global multiplier: 1.2 = 20% faster
    enter_s: float = 0.9         # duration of one element's entrance
    word_stagger_s: float = 0.07 # delay between words in kinetic headlines
    element_gap_s: float = 0.22  # delay between consecutive elements
    first_delay_s: float = 0.25
    slide_px: int = 36
    easing: str = "ease_out_quart"
    exit_s: float = 0.45
    drift_px: int = 14           # slow vertical drift of the whole composition per scene
    transition: str = "wipe_up"  # "wipe_up" | "fade" | "cut"
    transition_s: float = 0.6
    count_up: bool = True        # big numbers count up from zero
    # Scene length = base + words * read + per extra element, clamped to [min, max].
    scene_base_s: float = 2.2
    read_s_per_word: float = 0.26
    per_item_s: float = 0.35
    scene_min_s: float = 3.4
    scene_max_s: float = 7.5


@dataclass(frozen=True)
class SceneTheme:
    background: str
    foreground: str   # main text
    accent: str       # highlights, numbers, accent rules
    muted: str        # secondary text
    line: str         # hairlines, frames, header


@dataclass(frozen=True)
class VisualStyle:
    name: str = "warm_strict"
    palette: Palette = field(default_factory=Palette)
    fonts: Fonts = field(default_factory=Fonts)
    type: TypeScale = field(default_factory=TypeScale)
    spacing: Spacing = field(default_factory=Spacing)
    motion: MotionConfig = field(default_factory=MotionConfig)
    themes: dict[str, SceneTheme] = field(default_factory=lambda: {
        "cream": SceneTheme(_P.cream, _P.warm_black, _P.burgundy, _P.olive, _P.olive),
        "paper": SceneTheme(_P.paper, _P.espresso, _P.burgundy, _P.dark_olive, _P.dark_olive),
        "burgundy": SceneTheme(_P.burgundy, _P.cream, _P.paper, _P.paper, _P.paper),
        "espresso": SceneTheme(_P.espresso, _P.cream, _P.paper, _P.paper, _P.paper),
        "olive": SceneTheme(_P.dark_olive, _P.cream, _P.paper, _P.paper, _P.paper),
    })
    # Which theme each scene template uses.
    scene_themes: dict[str, str] = field(default_factory=lambda: {
        "statement": "cream",
        "big_number": "burgundy",
        "comparison": "cream",
        "list": "cream",
        "timeline": "paper",
        "quote": "espresso",
        "diagram": "cream",
        "split": "cream",
        "conclusion": "olive",
    })
    grain: int = 4               # paper texture strength, 0 to disable
    show_header: bool = True     # "03 / 09" + title at the top
    show_progress: bool = True   # thin progress line at the bottom

    def theme_for(self, kind: str) -> SceneTheme:
        return self.themes[self.scene_themes.get(kind, "cream")]


WARM_STRICT = VisualStyle()
DEFAULT_STYLE = WARM_STRICT


def load_style(path: str | Path, base: VisualStyle = DEFAULT_STYLE) -> VisualStyle:
    """Apply a JSON file of overrides (any subset of VisualStyle's fields) to `base`."""
    return _merge(base, json.loads(Path(path).read_text(encoding="utf-8")))


def _merge(obj, overrides: dict):
    updates = {}
    for key, value in overrides.items():
        if not hasattr(obj, key):
            raise KeyError(f"Unknown style setting: {type(obj).__name__}.{key}")
        current = getattr(obj, key)
        if is_dataclass(current) and isinstance(value, dict):
            value = _merge(current, value)
        elif isinstance(current, dict) and isinstance(value, dict):
            merged = dict(current)
            for k, v in value.items():
                if k in current and is_dataclass(current[k]) and isinstance(v, dict):
                    merged[k] = _merge(current[k], v)
                elif key == "themes" and isinstance(v, dict):
                    merged[k] = SceneTheme(**v)
                else:
                    merged[k] = v
            value = merged
        elif isinstance(current, tuple) and isinstance(value, list):
            value = tuple(value)
        updates[key] = value
    return replace(obj, **updates)


def hex_to_rgb(color: str) -> tuple[int, int, int]:
    color = color.lstrip("#")
    return tuple(int(color[i:i + 2], 16) for i in (0, 2, 4))
