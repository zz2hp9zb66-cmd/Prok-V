"""Plain data objects passed between pipeline stages.

Every stage consumes and produces these types, so a stage implementation can be
swapped (e.g. placeholder -> real image model) without touching the others.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from prokv.config import VideoSpec


@dataclass
class GeneratedImage:
    """An image produced by the generation stage."""

    path: Path
    prompt: str
    width: int
    height: int


@dataclass
class Layer:
    """One image placed on the canvas (pixel coordinates, top-left origin)."""

    id: str
    image: GeneratedImage
    x: int
    y: int
    width: int
    height: int
    rotation: float = 0.0
    z: int = 0


@dataclass
class Composition:
    """The static collage: a canvas plus its layers."""

    spec: VideoSpec
    layers: list[Layer]
    background: str = "#F4EFE6"


@dataclass
class Keyframe:
    """Transform of a layer at a moment in time, relative to its resting position."""

    time_s: float
    offset_x: float = 0.0
    offset_y: float = 0.0
    scale: float = 1.0
    rotation: float = 0.0
    opacity: float = 1.0


@dataclass
class Animation:
    """Keyframes for each layer, keyed by layer id."""

    tracks: dict[str, list[Keyframe]] = field(default_factory=dict)


@dataclass
class Caption:
    """User-supplied text shown on screen for a time range."""

    text: str
    start_s: float
    end_s: float
    position: str = "bottom"  # "top" | "center" | "bottom"


@dataclass
class Project:
    """Everything the export stage needs to produce the final video."""

    prompt: str
    spec: VideoSpec
    composition: Composition
    animation: Animation
    captions: list[Caption]
