"""Wires the stages together: prompt -> images -> collage -> animation -> captions -> export."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from prokv.animation import Animator, StaggeredRevealAnimator
from prokv.captions import build_captions
from prokv.composition import Compositor, StaggeredCollageCompositor
from prokv.config import VideoSpec
from prokv.export import Exporter, VideoExporter
from prokv.generation import ImageGenerator, PlaceholderGenerator
from prokv.models import Project


@dataclass
class Pipeline:
    """Each stage is pluggable; defaults are free, offline placeholders."""

    generator: ImageGenerator = field(default_factory=PlaceholderGenerator)
    compositor: Compositor = field(default_factory=StaggeredCollageCompositor)
    animator: Animator = field(default_factory=StaggeredRevealAnimator)
    exporter: Exporter = field(default_factory=VideoExporter)
    spec: VideoSpec = field(default_factory=VideoSpec)

    def run(
        self,
        prompt: str,
        captions: list[str] | None = None,
        out_dir: Path = Path("output"),
        image_count: int = 4,
    ) -> Path:
        if image_count < 1:
            raise ValueError("image_count must be at least 1")
        images = self.generator.generate(prompt, image_count, out_dir / "images")
        composition = self.compositor.compose(images, self.spec)
        animation = self.animator.animate(composition, self.spec)
        project = Project(
            prompt=prompt,
            spec=self.spec,
            composition=composition,
            animation=animation,
            captions=build_captions(captions or [], self.spec),
        )
        return self.exporter.export(project, out_dir)
