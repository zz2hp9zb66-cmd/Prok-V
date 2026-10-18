"""Script -> scenes and pace-based timing.

The split is deterministic: one paragraph = one scene; a paragraph that would
run longer than MAX_SCENE_SEC is split on sentence boundaries. The visual plan
(what to show) is filled in by Claude Code afterwards, see .claude/commands.
"""

from __future__ import annotations

import re

from .schemas import Pace, Scene, Timeline, TimelineEntry, Transition

# Words per minute of a future voice-over, per language and pace.
WPM: dict[str, dict[str, int]] = {
    "ru": {"slow": 110, "medium": 130, "fast": 150},
    "en": {"slow": 130, "medium": 150, "fast": 175},
}
MIN_SCENE_SEC: dict[str, float] = {"slow": 4.0, "medium": 3.0, "fast": 2.0}
MAX_SCENE_SEC = 9.0
# Extra time for objects to land before the first word and to breathe after the last.
PAD_SEC: dict[str, float] = {"slow": 1.2, "medium": 0.8, "fast": 0.4}
TRANSITION_FRAMES: dict[str, int] = {"slow": 18, "medium": 12, "fast": 8}

_SENTENCE = re.compile(r"(?<=[.!?…])\s+(?=[A-ZА-ЯЁ«\"—])")


def count_words(text: str) -> int:
    return len(re.findall(r"[\w’'-]+", text))


def scene_seconds(text: str, pace: Pace, language: str = "ru") -> float:
    wpm = WPM.get(language, WPM["en"])[pace]
    spoken = count_words(text) / wpm * 60
    return max(MIN_SCENE_SEC[pace], spoken + PAD_SEC[pace])


def split_script(text: str, pace: Pace, language: str = "ru") -> list[str]:
    body = "\n".join(line for line in text.splitlines() if not line.lstrip().startswith("#"))
    paragraphs = [re.sub(r"\s+", " ", p).strip() for p in re.split(r"\n\s*\n", body)]
    chunks: list[str] = []
    for para in filter(None, paragraphs):
        if scene_seconds(para, pace, language) <= MAX_SCENE_SEC:
            chunks.append(para)
            continue
        current = ""
        for sentence in _SENTENCE.split(para):
            candidate = f"{current} {sentence}".strip()
            if current and scene_seconds(candidate, pace, language) > MAX_SCENE_SEC:
                chunks.append(current)
                current = sentence
            else:
                current = candidate
        if current:
            chunks.append(current)
    return chunks


def build_scenes(text: str, pace: Pace, language: str, seed: int) -> list[Scene]:
    return [
        Scene(id=f"{i:02d}", index=i, text=chunk, words=count_words(chunk), seed=seed * 100 + i)
        for i, chunk in enumerate(split_script(text, pace, language), start=1)
    ]


def build_timeline(scenes: list[Scene], pace: Pace, language: str, fps: int, old: Timeline | None = None) -> Timeline:
    """Durations from text length. Entries marked `locked` in `old` keep their duration."""
    previous = {e.scene: e for e in old.entries} if old else {}
    entries = []
    for scene in scenes:
        prev = previous.get(scene.id)
        if prev and prev.locked:
            entries.append(prev)
            continue
        frames = round(scene_seconds(scene.text, pace, language) * fps)
        transition = prev.transition_out if prev else Transition(frames=TRANSITION_FRAMES[pace])
        entries.append(TimelineEntry(scene=scene.id, duration_frames=frames, transition_out=transition))
    return Timeline(fps=fps, pace=pace, entries=entries)
