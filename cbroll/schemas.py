"""Data models. Everything a project knows lives in these JSON-serialisable models."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

Pace = Literal["slow", "medium", "fast"]
SceneStatus = Literal["draft", "needs_changes", "approved"]
LicenseStatus = Literal["allowed", "manual_review", "forbidden", "test_placeholder"]
LayerKind = Literal["background", "photo", "cutout", "text", "shape", "texture"]


class Project(BaseModel):
    name: str
    title: str = ""
    language: str = "ru"
    pace: Pace = "medium"
    fps: int = 30
    width: int = 1080
    height: int = 1920
    seed: int = 1
    palette: dict[str, str] = Field(
        default_factory=lambda: {
            "paper": "#efe6d2",
            "ink": "#151515",
            "blue": "#1d3f8f",
            "accent": "#e2572b",
            "cream": "#f6efdf",
        }
    )


class Subject(BaseModel):
    """One visual the scene needs, as planned from the script."""

    slot: str
    kind: Literal["person", "object", "place", "document"]
    query: str
    role: Literal["hero", "prop", "background"] = "prop"
    asset: str | None = None  # chosen asset id
    label: str | None = None  # name tag shown next to the subject


class VisualPlan(BaseModel):
    subjects: list[Subject] = Field(default_factory=list)
    headline: str = ""
    caption: str = ""
    mood: str = ""


class Animation(BaseModel):
    """How a layer moves. Timings are in frames relative to the scene start."""

    enter: str = "fade"
    delay: int = 0
    duration: int = 14
    idle: str = "drift"


class Layer(BaseModel):
    id: str
    kind: LayerKind
    asset: str | None = None  # path relative to the project dir
    text: str | None = None
    font: str | None = None
    font_size: int | None = None
    color: str | None = None
    bg: str | None = None  # fill for text strips / shapes
    shape: str | None = None  # "torn_strip", "circle", "rect"
    x: float = 540  # centre, px
    y: float = 960
    w: float = 600  # width, px (height follows the asset aspect ratio)
    h: float | None = None  # only for shapes / text boxes
    rotation: float = 0
    z: int = 0
    depth: float = 0.5  # 0 = far, 1 = near; drives parallax
    opacity: float = 1
    shadow: bool = True
    tape: bool = False
    blend: str | None = None  # CSS mix-blend-mode
    anim: Animation = Field(default_factory=Animation)


class Camera(BaseModel):
    move: str = "push_in"  # push_in, pull_out, pan_left, pan_right, tilt_up, drift
    strength: float = 1.0


class Scene(BaseModel):
    id: str
    index: int
    text: str
    words: int = 0
    status: SceneStatus = "draft"
    notes: list[str] = Field(default_factory=list)
    plan: VisualPlan = Field(default_factory=VisualPlan)
    template: str | None = None  # see compose.TEMPLATES
    seed: int = 1
    background: str | None = None  # path to paper texture
    layers: list[Layer] = Field(default_factory=list)
    camera: Camera = Field(default_factory=Camera)


class Transition(BaseModel):
    type: str = "fade"  # fade, slide, wipe, paper_tear, zoom
    frames: int = 12


class TimelineEntry(BaseModel):
    scene: str
    duration_frames: int
    locked: bool = False  # set when the duration was edited by hand
    transition_out: Transition = Field(default_factory=Transition)


class Timeline(BaseModel):
    fps: int = 30
    pace: Pace = "medium"
    entries: list[TimelineEntry] = Field(default_factory=list)


class AssetMeta(BaseModel):
    id: str
    title: str = ""
    query: str = ""
    source: str = ""  # wikimedia, openverse, loc, test_generator, user
    url: str = ""
    author: str = ""
    license: str = ""
    license_url: str = ""
    status: LicenseStatus = "manual_review"
    original: str = ""  # relative path, never modified
    cut: bool = True  # False for photos used whole (backgrounds, covers)
    tone: str | None = None  # duotone for whole photos: blue, sepia, ink
    models: list[str] = Field(default_factory=list)  # segmentation override, merged as a union
    cutout: str | None = None
    styled: str | None = None
    width: int = 0
    height: int = 0
