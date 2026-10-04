"""Stage 3: animate the collage layers (keyframes only; rendering happens at export)."""

from __future__ import annotations

from abc import ABC, abstractmethod

from prokv.config import VideoSpec
from prokv.models import Animation, Composition, Keyframe


class Animator(ABC):
    """Produces per-layer keyframes for a composition."""

    @abstractmethod
    def animate(self, composition: Composition, spec: VideoSpec) -> Animation:
        ...


class StaggeredRevealAnimator(Animator):
    """Each layer slides up and fades in, one after another, then holds."""

    def __init__(self, reveal_s: float = 0.6, slide_px: float = 80.0) -> None:
        self.reveal_s = reveal_s
        self.slide_px = slide_px

    def animate(self, composition: Composition, spec: VideoSpec) -> Animation:
        tracks = {}
        for i, layer in enumerate(composition.layers):
            start = min(i * self.reveal_s, spec.duration_s)
            end = min(start + self.reveal_s, spec.duration_s)
            tracks[layer.id] = [
                Keyframe(start, offset_y=self.slide_px, scale=0.94, opacity=0.0),
                Keyframe(end),
                Keyframe(spec.duration_s),
            ]
        return Animation(tracks)
