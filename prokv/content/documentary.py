"""Documentary Reels: a fixed timeline of scenes with three information layers.

Layer 1 — narration (voice), layer 2 — music cards (ARTIST / TRACK / YEAR),
layer 3 — on-screen facts the viewer reads. One JSON file per video (see
examples/documentary/). Scene visuals are chosen by `visual.type` and drawn by
prokv/layout/documentary/.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

from prokv.content.track_map import parse_time


@dataclass
class Card:
    artist: str
    track: str
    year: str


@dataclass
class DocScene:
    start: float
    end: float
    kicker: str
    title: str
    narration: str                       # what the voice says (as written in the script)
    visual: dict
    year: int | None = None              # where the decade timeline marker points
    tts: str | None = None               # spoken form when it differs (names in Cyrillic, no digits)
    cards: list[Card] = field(default_factory=list)
    cards_at: list[float] | None = None  # seconds from scene start; default schedule otherwise
    card_s: float = 3.0                  # how long each card stays (2–4 s)
    fact: str = ""
    fact_at: float | None = None
    voice_at: float | None = None        # seconds from scene start; default: the documentary's lead

    @property
    def length(self) -> float:
        return self.end - self.start

    @property
    def spoken(self) -> str:
        return self.tts or self.narration


@dataclass
class Documentary:
    id: str
    output: str
    scenes: list[DocScene]
    timeline: tuple[int, int] = (1990, 2000)
    speaker: str = "eugene"
    narration_lead_s: float = 0.7        # title first, then the voice
    music_cues: str | None = None        # path to the music cue config (relative to the JSON)
    sources: list[str] = field(default_factory=list)
    notes: dict = field(default_factory=dict)
    path: Path | None = None

    @property
    def duration(self) -> float:
        return self.scenes[-1].end

    @classmethod
    def load(cls, path: str | Path) -> "Documentary":
        path = Path(path)
        data = json.loads(path.read_text(encoding="utf-8"))
        scenes = []
        for s in data.pop("scenes"):
            s = dict(s)
            s["start"], s["end"] = parse_time(s["start"]), parse_time(s["end"])
            s["cards"] = [Card(**c) for c in s.get("cards", [])]
            scenes.append(DocScene(**s))
        if "timeline" in data:
            data["timeline"] = tuple(data["timeline"])
        doc = cls(scenes=scenes, path=path, **data)
        doc.validate()
        return doc

    def music_cue_path(self) -> Path | None:
        if not self.music_cues:
            return None
        return (self.path.parent / self.music_cues).resolve() if self.path else Path(self.music_cues)

    def validate(self) -> None:
        from prokv.layout.documentary import VISUALS

        t = 0.0
        for i, sc in enumerate(self.scenes, 1):
            where = f"scene {i} ({sc.title})"
            if abs(sc.start - t) > 1e-6:
                raise ValueError(f"{where}: starts at {sc.start}s, previous ends at {t}s")
            if sc.end <= sc.start:
                raise ValueError(f"{where}: end must be after start")
            if sc.visual.get("type") not in VISUALS:
                raise ValueError(f"{where}: unknown visual {sc.visual.get('type')!r}; "
                                 f"available: {', '.join(sorted(VISUALS))}")
            if not 2.0 <= sc.card_s <= 4.0:
                raise ValueError(f"{where}: card_s must be 2–4 s")
            if sc.cards_at is not None and len(sc.cards_at) != len(sc.cards):
                raise ValueError(f"{where}: cards_at needs one time per card")
            if re.search(r"[0-9A-Za-z]", sc.spoken):
                raise ValueError(f"{where}: the spoken text has digits or Latin letters — Silero would "
                                 f"skip them; add a 'tts' field with words / Cyrillic")
            t = sc.end
