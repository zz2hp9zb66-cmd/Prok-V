"""Build a photo-led documentary Reels end to end, with quality checks.

    python -m prokv --story blue_note_reels/blue_note_scenario.json

Steps: load scenario + image manifest → voice per scene (Silero, if available)
→ scene timing follows the speech → voice track → subtitles (separate,
switchable track + .srt) → music bed (if a licensed file is present) → render
→ export → ffprobe → control frames → qc_report.md. Without TTS the video is
still produced, as *_PREVIEW_NO_VOICE.mp4, with estimated timings.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path

from PIL import Image

from prokv.config import VideoSpec
from prokv.content.image_story import ImageStory
from prokv.content.track_map import parse_time
from prokv.export import encode_mp4
from prokv.export.soundtrack import Cue, mix_soundtrack
from prokv.layout.image_story import auto_fixes, build_story, check_text_bounds
from prokv.render.stage_renderer import StageRenderer
from prokv.voice.silero import SileroTTS, VoiceConfig, write_wav

CHARS_PER_S = 14.5


def _estimate(text: str, pause: float) -> float:
    return len(text) / CHARS_PER_S + pause * max(0, len(re.findall(r"[.!?…]+", text)) - 1)


def _srt_time(t: float) -> str:
    ms = int(round(t * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def write_srt(path: Path, cues: list[tuple[float, float, str]]) -> Path:
    lines = []
    for i, (a, b, text) in enumerate(cues, 1):
        lines += [str(i), f"{_srt_time(a)} --> {_srt_time(b)}", text, ""]
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


def _subtitle_cues(text: str, start: float, length: float) -> list[tuple[float, float, str]]:
    """Sentences timed in proportion to their length inside the spoken segment."""
    sentences = [s for s in re.split(r"(?<=[.!?…])\s+", text) if s]
    total = sum(len(s) for s in sentences) or 1
    cues, t = [], start
    for s in sentences:
        d = length * len(s) / total
        cues.append((t, t + d, s))
        t += d
    return cues


def _ffprobe(path: Path) -> dict:
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
                          "stream=index,codec_type,codec_name,width,height,r_frame_rate,sample_rate,channels,duration:"
                          "format=duration,size", "-of", "json", str(path)],
                         capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def render_story(scenario: Path, speaker: str | None = None, use_voice: bool = True, fps: int = 30) -> Path:
    story = ImageStory.load(scenario)
    root = story.root
    audio_dir, renders, out_dir = root / "audio", root / "renders", root / "output"
    for d in (audio_dir, renders, out_dir, renders / "control_frames"):
        d.mkdir(parents=True, exist_ok=True)
    spec = VideoSpec(fps=fps)

    # -- voice ---------------------------------------------------------------
    tts, reason = None, "disabled (--no-voice)"
    if use_voice:
        try:
            tts = SileroTTS(VoiceConfig(speaker=speaker or story.speaker, pause_s=story.sentence_pause_s))
            tts.load()
        except Exception as error:
            tts, reason = None, f"{type(error).__name__}: {error}"
    rate = tts.config.sample_rate if tts else 48000
    clips, lengths = [], []
    for sc in story.scenes:
        (audio_dir / f"{sc.id}.txt").write_text(sc.narration + "\n", encoding="utf-8")
        if tts:
            clip = tts.speak(sc.spoken)
            write_wav(audio_dir / f"{sc.id}.wav", clip, rate)
            clips.append(clip)
            lengths.append(len(clip) / rate)
        else:
            clips.append(None)
            lengths.append(_estimate(sc.spoken, story.sentence_pause_s))

    # -- timing: each scene at least its planned length, longer if the speech needs it
    timing, t = [], 0.0
    for sc, speech in zip(story.scenes, lengths):
        length = max(sc.planned_length, story.voice_lead_s + speech + story.voice_tail_s)
        timing.append((t, t + length))
        t += length
    duration = t
    voice_wav = None
    if tts:
        track: list[float] = []
        for (s, _), clip in zip(timing, clips):
            track.extend([0.0] * (int(round((s + story.voice_lead_s) * rate)) - len(track)))
            track.extend(clip)
        track.extend([0.0] * max(0, int(round(duration * rate)) - len(track)))
        voice_wav = write_wav(audio_dir / "voice.wav", track, rate)

    # -- subtitles (separate, switchable) ----------------------------------------
    subs = []
    for sc, (s, _), speech in zip(story.scenes, timing, lengths):
        subs += _subtitle_cues(sc.narration, s + story.voice_lead_s, speech)
    stem = Path(story.output).stem if tts else Path(story.output).stem.replace("FINAL", "PREVIEW_NO_VOICE")
    srt = write_srt(out_dir / f"{stem}.ru.srt", subs)

    # -- music -----------------------------------------------------------------------
    cues, music_note = [], "no music config"
    cfg_path = root / story.music.get("config", "assets/music/music.json")
    if cfg_path.exists():
        for c in json.loads(cfg_path.read_text(encoding="utf-8")).get("cues", []):
            end = duration if c.get("end") == "auto" else parse_time(c["end"])
            file = (cfg_path.parent / c["file"]).resolve() if c.get("file") else None
            cues.append(Cue(c.get("artist", ""), c.get("track", ""), parse_time(c.get("start", 0)), end,
                            str(file) if file else None, c.get("offset", 0.0), c.get("gain_db", -20.0),
                            c.get("fade_s", 1.0)))
    soundtrack, used, missing_music = mix_soundtrack(duration, audio_dir / "soundtrack.wav", voice_wav, cues,
                                                     fade_out_s=1.2)
    music_note = (f"{len(used)} music file(s) mixed" if used else
                  f"no licensed music file found ({', '.join(Path(c.file).name for c in missing_music if c.file)})")

    # -- picture -----------------------------------------------------------------------
    stage, overlay, texts = build_story(story, timing, spec)
    bounds = check_text_bounds(texts)
    fixes = auto_fixes(texts)
    renderer = StageRenderer(stage, fps, 3, overlay)
    frames = []
    for sc, (s, e) in zip(story.scenes, timing):
        for frac in (0.25, 0.85):
            frame = renderer.render(s + (e - s) * frac)
            frame.save(renders / "control_frames" / f"{sc.id}_{int(frac * 100):02d}.png")
            frames.append(frame)
    _contact_sheet(frames, renders / "control_frames" / "contact_sheet.png")

    silent = renders / f"{stem}_no_subs.mp4"
    encode_mp4(renderer.frames(), spec, silent, audio=soundtrack)
    final = out_dir / f"{stem}.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(silent), "-i", str(srt), "-map", "0", "-map", "1",
                    "-c", "copy", "-c:s", "mov_text", "-metadata:s:s:0", "language=rus",
                    "-disposition:s:0", "0", "-movflags", "+faststart", str(final)], check=True)

    # -- checks & report -------------------------------------------------------------------
    probe = _ffprobe(final)
    (renders / "render_config.json").write_text(json.dumps({
        "scenario": str(scenario), "fps": fps, "size": [spec.width, spec.height], "video": "H.264 (libx264, crf 18)",
        "audio": "AAC 192k", "subtitles": "mov_text (off by default) + .srt",
        "voice": {"engine": "Silero", "speaker": speaker or story.speaker, "available": bool(tts), "reason": reason},
        "timing": [{"scene": sc.id, "start": round(s, 2), "end": round(e, 2), "planned": [sc.start, sc.end],
                    "speech_s": round(sp, 2), "speech_measured": bool(tts)}
                   for sc, (s, e), sp in zip(story.scenes, timing, lengths)],
        "duration": round(duration, 2), "music": music_note,
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    _report(story, timing, lengths, bool(tts), reason, bounds, probe, music_note, final, srt, out_dir, fixes)
    return final


def _contact_sheet(frames: list[Image.Image], path: Path) -> None:
    thumbs = [f.resize((216, 384), Image.Resampling.LANCZOS) for f in frames]
    cols = 7
    rows = (len(thumbs) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * 222 + 6, rows * 390 + 6), "#888888")
    for i, th in enumerate(thumbs):
        sheet.paste(th, (6 + (i % cols) * 222, 6 + (i // cols) * 390))
    sheet.save(path)


def _report(story, timing, lengths, measured, reason, bounds, probe, music_note, final, srt, out_dir,
            fixes=()) -> None:
    v = next(s for s in probe["streams"] if s["codec_type"] == "video")
    a = next((s for s in probe["streams"] if s["codec_type"] == "audio"), None)
    sub = next((s for s in probe["streams"] if s["codec_type"] == "subtitle"), None)
    dur = float(probe["format"]["duration"])
    ok = lambda c: "✅" if c else "❌"  # noqa: E731
    lines = [f"# QC report — {story.title}", "",
             f"File: `{final.name}` · {int(probe['format']['size']) / 1e6:.1f} MB · {dur:.2f} s", "",
             "## Automatic checks (run during this build)", "",
             f"- {ok(v['codec_name'] == 'h264' and (v['width'], v['height']) == (1080, 1920))} Video: "
             f"{v['codec_name']} {v['width']}×{v['height']} @ {v['r_frame_rate']}",
             f"- {ok(a and a['codec_name'] == 'aac')} Audio: {a['codec_name'] if a else 'none'} "
             f"{a.get('sample_rate', '') if a else ''} Hz",
             f"- {ok(sub is not None)} Subtitles: separate switchable mov_text track + `{srt.name}` "
             f"(the MP4 muxer flags it as default; some players may show it automatically — "
             f"`renders/*_no_subs.mp4` has no subtitle track)",
             f"- {ok(not story.missing)} Images: {len(story.images) - len(story.missing)}/{len(story.images)} found by ID"
             + (f"; placeholders for {', '.join(i.id for i in story.missing)}" if story.missing else ""),
             f"- {ok(not bounds)} Text inside the Reels safe area (x 60–1020, y 250–1490): "
             + ("all text blocks inside" if not bounds else f"{len(bounds)} problem(s)"),
             f"- Text auto-fixes: " + ("none needed" if not fixes else "; ".join(fixes)),
             f"- {ok(measured)} Voice: " + ("Silero, measured per scene" if measured else f"not generated — {reason}"),
             f"- {ok(measured)} Speech ↔ picture sync: " + ("scene lengths follow the measured speech" if measured
                                                         else "NOT checked — timings are estimates without TTS"),
             f"- Music: {music_note}", "",
             "## Scenes", "", "| Scene | Planned | Final | Speech | Voice from |", "|---|---|---|---|---|"]
    for sc, (s, e), sp in zip(story.scenes, timing, lengths):
        lines.append(f"| {sc.id} {sc.title} | {sc.start:.0f}–{sc.end:.0f} s ({sc.planned_length:.0f} s) | "
                     f"{s:.1f}–{e:.1f} s ({e - s:.1f} s) | {sp:.1f} s{'' if measured else ' (est.)'} | "
                     f"{s + story.voice_lead_s:.1f} s |")
    lines += ["", f"Total: {timing[-1][1]:.1f} s (target ≈76 s).", ""]
    if bounds:
        lines += ["## Text outside the safe area", ""] + [f"- {b}" for b in bounds] + [""]
    lines += ["## Images", "", "| ID | File | Status | Used in |", "|---|---|---|---|"]
    for img in story.images.values():
        lines.append(f"| {img.id} | {img.path.name if img.path else img.file} | "
                     f"{'found ' + 'x'.join(map(str, img.size)) if img.found else 'MISSING → placeholder'} | "
                     f"{', '.join(img.scenes)} |")
    lines += ["", "## Notes on facts", ""] + [f"- **{k}**: {v}" for k, v in story.notes.items()]
    lines += ["", "## Sources", ""] + [f"- {s}" for s in story.sources]
    lines += ["", "## Not checked automatically", "",
              "- How the voice sounds (pronunciation, intonation) — listen to `audio/voice.wav`.",
              "- Visual taste and image–ID correspondence beyond file names — see `renders/control_frames/`."]
    (out_dir / "qc_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
