"""Data for the "Карта одного трека" (one-track map) series.

One JSON file per episode (see examples/maps/). Only facts and on-screen text
live here; the choreography is in prokv/layout/track_map.py.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Person:
    name: str
    role: str


@dataclass
class Musician:
    instrument: str          # on-screen label, e.g. "RHODES / SYNTH"
    name: str
    texture: str             # drums | bass | guitar | rhodes | synth | lyricon


@dataclass
class Afterlife:
    artist: str
    year: str
    note: str = ""           # e.g. "drums sampled" — kept in the data for sourcing


@dataclass
class TrackMap:
    number: int
    track: str
    artist: str
    album: str
    year: str
    label: str
    city: str
    studio: str
    recorded: str
    people: list[Person]
    musicians: list[Musician]
    core: list[str]                      # the two instruments of "the turn", e.g. ["DRUMS", "BASS"]
    afterlife: list[Afterlife]
    influence_inner: list[str]
    influence_outer: list[str]
    series: str = "КАРТА ОДНОГО ТРЕКА"
    subtitle: str = "ANATOMY OF A RECORD"
    hook: list[str] = field(default_factory=lambda: ["ТЫ УЗНАЕШЬ ЕГО", "ЗА НЕСКОЛЬКО СЕКУНД."])
    hook_question: str = "НО КТО СОЗДАЛ ЭТОТ ЗВУК?"
    people_outro: str = "THAT'S ONLY THE BEGINNING."
    turn_text: list[str] = field(default_factory=lambda: ["И ВОТ ПОЧЕМУ", "ТЕБЕ ХВАТАЕТ ПАРЫ СЕКУНД."])
    turn_pair: str = ""
    afterlife_question: str = "WHAT HAPPENED NEXT?"
    afterlife_caption: str = "SAMPLED · REUSED · REINTERPRETED"
    outro: list[str] = field(default_factory=lambda: ["ONE SONG.", "DOZENS OF CONNECTIONS."])
    cta: str = "What should we map next?"
    bpm: float = 120.0
    cover_image: str | None = None       # optional path; a typographic sleeve is drawn otherwise
    sources: list[str] = field(default_factory=list)

    @classmethod
    def load(cls, path: str | Path) -> "TrackMap":
        path = Path(path)
        data = json.loads(path.read_text(encoding="utf-8"))
        data["people"] = [Person(**p) for p in data["people"]]
        data["musicians"] = [Musician(**m) for m in data["musicians"]]
        data["afterlife"] = [Afterlife(**a) for a in data["afterlife"]]
        if data.get("cover_image"):
            data["cover_image"] = str((path.parent / data["cover_image"]).resolve())
        tm = cls(**data)
        tm.validate()
        return tm

    def validate(self) -> None:
        if not 1 <= len(self.people) <= 3:
            raise ValueError("people: 1–3 entries (they form the triangle)")
        if not 2 <= len(self.musicians) <= 6:
            raise ValueError("musicians: 2–6 entries")
        if not 1 <= len(self.afterlife) <= 3:
            raise ValueError("afterlife: 1–3 entries")
        names = {m.instrument for m in self.musicians}
        missing = [c for c in self.core if c not in names]
        if len(self.core) != 2 or missing:
            raise ValueError(f"core must name two musicians' instruments; unknown: {missing}")
