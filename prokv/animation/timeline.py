"""Scene timing: hands out start times for consecutive elements."""

from __future__ import annotations

from prokv.style import MotionConfig


class Sequencer:
    """Cursor over a scene's timeline. All times are scaled by MotionConfig.speed."""

    def __init__(self, config: MotionConfig) -> None:
        self.config = config
        self.t = config.first_delay_s / config.speed

    def dur(self, seconds: float) -> float:
        return seconds / self.config.speed

    @property
    def enter(self) -> float:
        return self.dur(self.config.enter_s)

    def next(self, gap: float | None = None) -> float:
        """Start time for the next element, then advance by `gap` (default element gap)."""
        start = self.t
        self.t += self.dur(self.config.element_gap_s if gap is None else gap)
        return start

    def words(self, count: int) -> list[float]:
        """Start times for a staggered word-by-word reveal."""
        step = self.dur(self.config.word_stagger_s)
        starts = [self.t + i * step for i in range(count)]
        self.t = (starts[-1] if starts else self.t) + self.dur(self.config.element_gap_s)
        return starts

    def wait(self, seconds: float) -> None:
        self.t += self.dur(seconds)
