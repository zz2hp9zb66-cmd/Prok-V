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
    """Layers appear one after another: each slides in from its side of the canvas,
    fades in and grows to full size, then drifts slowly until the end of the video."""

    def __init__(
        self,
        start_delay_s: float = 0.2,
        stagger_s: float = 0.45,
        reveal_s: float = 0.8,
        slide_px: float = 140.0,
        drift_px: float = 40.0,
        drift_scale: float = 1.04,
    ) -> None:
        self.start_delay_s = start_delay_s
        self.stagger_s = stagger_s
        self.reveal_s = reveal_s
        self.slide_px = slide_px
        self.drift_px = drift_px
        self.drift_scale = drift_scale

    def animate(self, composition: Composition, spec: VideoSpec) -> Animation:
        tracks = {}
        end_s = spec.duration_s
        for i, layer in enumerate(composition.layers):
            from_left = layer.x + layer.width / 2 < spec.width / 2
            direction = -1 if from_left else 1
            start = min(self.start_delay_s + i * self.stagger_s, end_s)
            settled = min(start + self.reveal_s, end_s)
            tracks[layer.id] = [
                Keyframe(0.0, offset_x=direction * self.slide_px, offset_y=self.slide_px / 2,
                         scale=0.9, opacity=0.0, easing="hold"),
                Keyframe(start, offset_x=direction * self.slide_px, offset_y=self.slide_px / 2,
                         scale=0.9, opacity=0.0, easing="ease_out"),
                Keyframe(settled, easing="linear"),
                Keyframe(end_s, offset_x=-direction * self.drift_px / 2, offset_y=-self.drift_px,
                         scale=self.drift_scale),
            ]
        return Animation(tracks)
