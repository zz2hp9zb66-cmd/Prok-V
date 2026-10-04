"""Global output settings."""

from dataclasses import dataclass


@dataclass(frozen=True)
class VideoSpec:
    """Target video format. Defaults to vertical 9:16 Full HD."""

    width: int = 1080
    height: int = 1920
    fps: int = 30
    duration_s: float = 10.0

    @property
    def aspect_ratio(self) -> str:
        return "9:16" if self.width * 16 == self.height * 9 else f"{self.width}:{self.height}"
