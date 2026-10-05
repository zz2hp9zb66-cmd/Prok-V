"""Plain data passed between stages: text -> Storyboard (scenes) -> video.

A Storyboard is saved as storyboard.json next to the video. It can be edited by
hand (texts, scene kinds, durations) and re-rendered with `--from-plan`.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field

from prokv.config import VideoSpec

SCENE_KINDS = (
    "statement",    # 01 one strong thought
    "big_number",   # 02 a key figure
    "comparison",   # 03 two sides
    "list",         # 04 enumerated points
    "timeline",     # 05 dated events
    "quote",        # 06 a quotation
    "diagram",      # 07 steps / cause -> effect
    "split",        # 08 term + explanation
    "conclusion",   # 09 the takeaway
)


@dataclass
class SceneContent:
    """Condensed, on-screen wording of one scene. Templates use the fields they need."""

    kicker: str = ""             # small label above the headline
    headline: str = ""
    body: str = ""               # secondary line
    number: str = ""             # display string, e.g. "+10%"
    items: list[str] = field(default_factory=list)          # list entries / diagram steps
    pairs: list[list[str]] = field(default_factory=list)    # [label, text]: timeline, comparison
    quote: str = ""
    author: str = ""
    highlights: list[str] = field(default_factory=list)     # words to emphasise


@dataclass
class Scene:
    kind: str
    duration_s: float
    content: SceneContent
    source: str = ""             # the original text this scene was made from
    variant: str = ""            # "" or "alt": alternative layout of the same template


@dataclass
class Storyboard:
    title: str
    language: str
    scenes: list[Scene]
    spec: VideoSpec = field(default_factory=VideoSpec)

    @property
    def duration_s(self) -> float:
        return sum(scene.duration_s for scene in self.scenes)

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> Storyboard:
        return cls(
            title=data["title"],
            language=data.get("language", "ru"),
            spec=VideoSpec(**data.get("spec", {})),
            scenes=[
                Scene(s["kind"], s["duration_s"], SceneContent(**s["content"]), s.get("source", ""),
                      s.get("variant", ""))
                for s in data["scenes"]
            ],
        )
