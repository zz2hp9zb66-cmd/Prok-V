"""Episodes of the "Карта одного трека" (one-track map) series.

One JSON file per episode (see examples/maps/): track facts plus a list of
timed sections. Times are seconds or "m:ss". Section types and their fields
are documented in prokv/layout/maps/ and the README.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path


def parse_time(value) -> float:
    if isinstance(value, (int, float)):
        return float(value)
    m = re.fullmatch(r"\s*(\d+):(\d{1,2}(?:\.\d+)?)\s*", str(value))
    if m:
        return int(m.group(1)) * 60 + float(m.group(2))
    return float(value)


@dataclass
class Section:
    type: str
    start: float
    end: float
    data: dict

    @property
    def length(self) -> float:
        return self.end - self.start


@dataclass
class Episode:
    number: int
    track: str
    artist: str
    album: str
    year: str
    label: str
    sections: list[Section]
    series: str = "КАРТА ОДНОГО ТРЕКА"
    bpm: float = 120.0
    sleeve_title: str | None = None   # text on the drawn sleeve (default: album)
    cover_image: str | None = None    # optional real cover (path relative to the JSON)
    sources: list[str] = field(default_factory=list)
    notes: dict = field(default_factory=dict)   # free-form research notes, not rendered

    @property
    def duration(self) -> float:
        return self.sections[-1].end if self.sections else 0.0

    @classmethod
    def load(cls, path: str | Path) -> "Episode":
        path = Path(path)
        data = json.loads(path.read_text(encoding="utf-8"))
        data["sections"] = [
            Section(s["type"], parse_time(s["start"]), parse_time(s["end"]),
                    {k: v for k, v in s.items() if k not in ("type", "start", "end")})
            for s in data["sections"]
        ]
        if data.get("cover_image"):
            data["cover_image"] = str((path.parent / data["cover_image"]).resolve())
        episode = cls(**data)
        episode.validate()
        return episode

    def validate(self) -> None:
        from prokv.layout.maps import SECTIONS  # registry of section types

        if not self.sections:
            raise ValueError("An episode needs at least one section")
        previous_end = 0.0
        for i, sec in enumerate(self.sections):
            where = f"section {i + 1} ({sec.type})"
            if sec.type not in SECTIONS:
                raise ValueError(f"{where}: unknown type. Available: {', '.join(sorted(SECTIONS))}")
            if sec.end <= sec.start:
                raise ValueError(f"{where}: end must be after start")
            if abs(sec.start - previous_end) > 1e-6:
                raise ValueError(f"{where}: starts at {sec.start}s, previous ends at {previous_end}s")
            previous_end = sec.end
            items = sec.data.get("items", [])
            limits = {"branches": (1, 3), "musicians": (2, 6), "afterlife": (1, 3), "coordinates": (1, 4),
                      "places": (1, 2), "awards": (1, 3)}
            if sec.type in limits:
                key = "places" if sec.type == "places" else "items"
                n = len(sec.data.get(key, items))
                lo, hi = limits[sec.type]
                if not lo <= n <= hi:
                    raise ValueError(f"{where}: needs {lo}–{hi} {key}, got {n}")
            if sec.type == "core":
                musicians = next((s for s in reversed(self.sections[:i]) if s.type == "musicians"), None)
                names = {m["instrument"] for m in (musicians.data["items"] if musicians else [])}
                missing = [c for c in sec.data.get("pair", []) if c not in names]
                if len(sec.data.get("pair", [])) != 2 or missing:
                    raise ValueError(f"{where}: 'pair' must name two instruments from the musicians section; "
                                     f"unknown: {missing}")


TrackMap = Episode  # backwards-compatible name
