"""text -> content analysis -> storyboard -> scene templates -> frames -> MP4."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from prokv.config import VideoSpec
from prokv.content.analyzer import ContentAnalyzer, RuleBasedAnalyzer
from prokv.export import encode_mp4, save_storyboard
from prokv.models import Storyboard
from prokv.render import StoryboardRenderer
from prokv.style import DEFAULT_STYLE, VisualStyle

STORYBOARD_NAME = "storyboard.json"
VIDEO_NAME = "video.mp4"


@dataclass
class Pipeline:
    """Every stage is replaceable: pass another analyzer or style."""

    style: VisualStyle = DEFAULT_STYLE
    spec: VideoSpec = field(default_factory=VideoSpec)
    analyzer: ContentAnalyzer | None = None
    max_scenes: int = 12

    def __post_init__(self) -> None:
        self.analyzer = self.analyzer or RuleBasedAnalyzer(self.style.motion, self.max_scenes)

    def plan(self, text: str) -> Storyboard:
        """Analyse text into a storyboard (scenes, templates, wording, timing)."""
        return self.analyzer.analyze(text, self.spec)

    def render(self, storyboard: Storyboard, out_path: Path) -> Path:
        renderer = StoryboardRenderer(storyboard, self.style)
        return encode_mp4(renderer.frames(), storyboard.spec, out_path)

    def run(self, text: str, out_dir: Path = Path("output"), plan_only: bool = False) -> Path:
        storyboard = self.plan(text)
        plan_path = save_storyboard(storyboard, out_dir / STORYBOARD_NAME)
        if plan_only:
            return plan_path
        return self.render(storyboard, out_dir / VIDEO_NAME)
