"""Voice track for documentary Reels: one Silero segment per scene, placed on the
fixed timeline.

Fitting rules (in this order): start the voice after the scene title; if a
segment is too long for its window, re-speak it with shorter pauses between
sentences; if it still does not fit, keep every word (no speed-up, no cuts) and
push the following segments later, and write a proposal for script edits.

Without PyTorch / the Silero model the segments are still written as text
files with estimated timings, so the video can be built and voiced later.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

from prokv.content.documentary import Documentary
from prokv.voice.silero import SileroTTS, VoiceConfig, write_wav

CHARS_PER_S = 14.5          # Silero's typical Russian pace, used only for estimates
MIN_GAP_S = 0.15


@dataclass
class Segment:
    index: int
    title: str
    spoken: str
    planned_start: float
    window_end: float
    start: float = 0.0
    length: float = 0.0
    estimated: bool = True
    pause_s: float = 0.35
    file: Path | None = None

    @property
    def window(self) -> float:
        return self.window_end - self.planned_start

    @property
    def overflow(self) -> float:
        return max(0.0, self.start + self.length - self.window_end)


@dataclass
class VoiceTrack:
    segments: list[Segment]
    wav: Path | None              # None when TTS is unavailable
    folder: Path
    reason: str = ""              # why TTS was not used
    notes: list[str] = field(default_factory=list)

    @property
    def available(self) -> bool:
        return self.wav is not None


def estimate(text: str, pause_s: float) -> float:
    sentences = max(1, len(re.findall(r"[.!?…]+", text)))
    return len(text) / CHARS_PER_S + pause_s * (sentences - 1)


def _plan(doc: Documentary) -> list[Segment]:
    plan = []
    for i, sc in enumerate(doc.scenes):
        lead = sc.voice_at if sc.voice_at is not None else doc.narration_lead_s
        if i + 1 < len(doc.scenes):
            nxt = doc.scenes[i + 1]
            nxt_lead = nxt.voice_at if nxt.voice_at is not None else doc.narration_lead_s
            end = nxt.start + nxt_lead - MIN_GAP_S
        else:
            end = doc.duration - 0.8      # before the final fade-out
        plan.append(Segment(i + 1, sc.title or sc.kicker or "Финал", sc.spoken, sc.start + lead, end))
    return plan


def build_voice_track(doc: Documentary, folder: Path, speaker: str | None = None,
                      tts: SileroTTS | None = None) -> VoiceTrack:
    folder.mkdir(parents=True, exist_ok=True)
    segments = _plan(doc)
    reason = ""
    if tts is None:
        try:
            tts = SileroTTS(VoiceConfig(speaker=speaker or doc.speaker))
            tts.load()
        except Exception as error:  # no PyTorch, no model, no network: build without voice
            tts, reason = None, f"{type(error).__name__}: {error}"
    rate = tts.config.sample_rate if tts else 48000
    clips: list[list[float]] = []
    cursor = 0.0
    for seg in segments:
        (folder / f"scene_{seg.index:02d}.txt").write_text(seg.spoken + "\n", encoding="utf-8")
        if tts:
            clip, seg.pause_s = _speak_to_fit(tts, seg)
            seg.length, seg.estimated = len(clip) / rate, False
            seg.file = write_wav(folder / f"scene_{seg.index:02d}.wav", clip, rate)
            clips.append(clip)
        else:
            seg.pause_s = 0.35 if estimate(seg.spoken, 0.35) <= seg.window else 0.18
            seg.length = estimate(seg.spoken, seg.pause_s)
        seg.start = max(seg.planned_start, cursor + MIN_GAP_S if cursor else seg.planned_start)
        cursor = seg.start + seg.length
    wav = None
    if tts:
        track: list[float] = []
        for seg, clip in zip(segments, clips):
            track.extend([0.0] * (int(round(seg.start * rate)) - len(track)))
            track.extend(clip)
        track.extend([0.0] * max(0, int(round(doc.duration * rate)) - len(track)))
        wav = write_wav(folder / "voice.wav", track, rate)
    result = VoiceTrack(segments, wav, folder, reason)
    _write_reports(doc, result)
    return result


def _speak_to_fit(tts: SileroTTS, seg: Segment) -> tuple[list[float], float]:
    """Speak with natural pauses; if too long, once more with shorter pauses."""
    rate = tts.config.sample_rate
    clip = tts.speak(seg.spoken)
    if len(clip) / rate <= seg.window:
        return clip, tts.config.pause_s
    tighter = SileroTTS(tts.config.with_(pause_s=0.18), model=tts.load())
    return tighter.speak(seg.spoken), 0.18


def _write_reports(doc: Documentary, track: VoiceTrack) -> None:
    kind = "measured" if track.available else "estimated"
    lines = [f"# Voiceover — {doc.id}", "",
             f"Voice: Silero {doc.speaker}. Durations are {kind}." +
             ("" if track.available else f" TTS unavailable: {track.reason}"), "",
             "| # | Scene | Voice starts | Length | Window | Fits |", "|---|---|---|---|---|---|"]
    for s in track.segments:
        fits = "yes" if s.overflow <= 0.01 else f"over by {s.overflow:.1f}s"
        lines.append(f"| {s.index} | {s.title} | {s.start:.1f}s | {s.length:.1f}s | {s.window:.1f}s | {fits} |")
    lines += ["", "## Text", ""]
    lines += [f"**{s.index}. {s.title}** ({s.start:.1f}s)  \n{s.spoken}\n" for s in track.segments]
    (track.folder / "narration.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    over = [s for s in track.segments if s.overflow > 0.01]
    proposal = track.folder / "edits_proposal.md"
    if over:
        out = ["# Proposed script edits", "",
               "These segments do not fit their scene even with shorter pauses. The voice was not",
               "sped up and nothing was cut; the following segments were pushed later instead.",
               "Shorter wording that keeps the meaning (edit `narration` in the scenario JSON):", ""]
        for s in over:
            suggestion = doc.notes.get("edits", {}).get(str(s.index), "— shorten by ~"
                                                           f"{int(s.overflow * CHARS_PER_S) + 5} characters")
            out += [f"## Scene {s.index}. {s.title} — over by {s.overflow:.1f}s", "",
                    f"Now: {s.spoken}", "", f"Proposal: {suggestion}", ""]
        proposal.write_text("\n".join(out), encoding="utf-8")
    elif proposal.exists():
        proposal.unlink()
