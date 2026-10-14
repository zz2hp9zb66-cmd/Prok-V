"""Voice a track-map episode scene by scene and fit the scenes to the speech.

Each section's "narration" text is spoken separately. A section is lengthened
when its speech (plus a short lead-in and tail) does not fit; it is never
shortened, the voice is never sped up and no sentence is cut. The speech
clips are then laid on one track so each starts with its own section.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path

from prokv.content.track_map import Episode
from prokv.voice.silero import SileroTTS, write_wav


@dataclass
class NarratedSection:
    type: str
    start: float          # section start in the new timing
    length: float         # new section length
    original_length: float
    speech_start: float
    speech_length: float
    text: str


@dataclass
class Narration:
    episode: Episode      # same episode with re-timed sections
    wav: Path
    text_file: Path
    sections: list[NarratedSection]

    @property
    def duration(self) -> float:
        return self.episode.duration


def narrate_episode(ep: Episode, tts: SileroTTS, wav_path: Path, lead_s: float = 0.35,
                    tail_s: float = 0.6) -> Narration:
    rate = tts.config.sample_rate
    track: list[float] = []
    sections, report = [], []
    t = 0.0
    for sec in ep.sections:
        text = sec.data.get("narration", "").strip()
        clip = tts.speak(text) if text else []
        speech = len(clip) / rate
        length = max(sec.length, lead_s + speech + tail_s) if clip else sec.length
        speech_start = t + lead_s
        if clip:
            track.extend([0.0] * (int(round(speech_start * rate)) - len(track)))
            track.extend(clip)
        sections.append(replace(sec, start=t, end=t + length))
        report.append(NarratedSection(sec.type, t, length, sec.length, speech_start, speech, text))
        t += length
    track.extend([0.0] * (int(round(t * rate)) - len(track)))
    write_wav(wav_path, track, rate)
    text_file = wav_path.with_suffix(".txt")
    text_file.write_text("\n\n".join(f"[{r.start:5.1f}s] {r.text}" for r in report if r.text) + "\n",
                         encoding="utf-8")
    return Narration(replace(ep, sections=sections), wav_path, text_file, report)
