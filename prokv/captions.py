"""Stage 4: turn user-supplied text into timed captions."""

from __future__ import annotations

from prokv.config import VideoSpec
from prokv.models import Caption


def build_captions(texts: list[str], spec: VideoSpec, position: str = "bottom") -> list[Caption]:
    """Split the video duration evenly between the given caption texts."""
    texts = [t.strip() for t in texts if t.strip()]
    if not texts:
        return []
    slot = spec.duration_s / len(texts)
    return [Caption(text, i * slot, (i + 1) * slot, position) for i, text in enumerate(texts)]
