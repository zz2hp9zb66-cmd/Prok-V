"""Stage 2: arrange images into an editorial/collage layout."""

from __future__ import annotations

from abc import ABC, abstractmethod

from prokv.config import VideoSpec
from prokv.models import Composition, GeneratedImage, Layer
from prokv.style import DEFAULT_STYLE, VisualStyle


class Compositor(ABC):
    """Places generated images on the vertical canvas."""

    @abstractmethod
    def compose(self, images: list[GeneratedImage], spec: VideoSpec) -> Composition:
        ...


class StaggeredCollageCompositor(Compositor):
    """Cascades images down the canvas, alternating left/right with a slight tilt."""

    def __init__(
        self,
        tile_ratio: float = 0.62,
        margin: int = 130,
        tilt: float = 1.5,
        style: VisualStyle = DEFAULT_STYLE,
    ) -> None:
        self.tile_ratio = tile_ratio
        self.margin = margin
        self.tilt = tilt
        self.background = style.background

    def compose(self, images: list[GeneratedImage], spec: VideoSpec) -> Composition:
        layers = []
        n = len(images)
        tile_w = int(spec.width * self.tile_ratio)
        usable_h = spec.height - 2 * self.margin
        for i, image in enumerate(images):
            tile_h = int(tile_w * image.height / image.width)
            step = (usable_h - tile_h) / (n - 1) if n > 1 else 0
            left = i % 2 == 0
            layers.append(
                Layer(
                    id=f"layer_{i:02d}",
                    image=image,
                    x=self.margin if left else spec.width - self.margin - tile_w,
                    y=int(self.margin + i * step),
                    width=tile_w,
                    height=tile_h,
                    rotation=-self.tilt if left else self.tilt,
                    z=i,
                )
            )
        return Composition(spec=spec, layers=layers, background=self.background)
