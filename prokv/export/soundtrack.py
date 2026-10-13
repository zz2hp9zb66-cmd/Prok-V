"""Mix the final soundtrack with FFmpeg: voice + licensed music cues.

Music cues come from a JSON config (see assets/music/*.cues.json). A cue whose
file is missing is skipped and reported — the slot simply stays silent, so the
timing is ready for when a legal audio file is added. Music sits under the voice
(gain_db, default −16 dB) with short fades. The result always exists and covers
the whole video, so the MP4 always gets an AAC track.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

from prokv.content.track_map import parse_time


@dataclass
class Cue:
    artist: str
    track: str
    start: float
    end: float
    file: str | None
    offset: float = 0.0          # where in the music file to start
    gain_db: float = -16.0
    fade_s: float = 0.4


def load_cues(path: Path | None) -> list[Cue]:
    if not path or not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    cues = []
    for c in data.get("cues", []):
        c = dict(c)
        c.pop("year", None)
        c.pop("note", None)
        c["start"], c["end"] = parse_time(c["start"]), parse_time(c["end"])
        file = c.get("file")
        if file and not Path(file).is_absolute():
            c["file"] = str((path.parent / file).resolve())
        cues.append(Cue(**c))
    return cues


def mix_soundtrack(duration: float, out_wav: Path, voice: Path | None = None, cues: list[Cue] | None = None,
                   fade_out_s: float = 0.7, binary: str = "ffmpeg") -> tuple[Path, list[Cue], list[Cue]]:
    """Returns (wav, used_cues, missing_cues)."""
    ffmpeg = shutil.which(binary)
    if ffmpeg is None:
        raise RuntimeError("FFmpeg not found")
    cues = cues or []
    used = [c for c in cues if c.file and Path(c.file).is_file()]
    missing = [c for c in cues if c not in used]
    inputs = ["-f", "lavfi", "-t", f"{duration:.3f}", "-i", "anullsrc=r=48000:cl=stereo"]
    labels = ["[0:a]"]
    filters = []
    n = 1
    if voice is not None:
        inputs += ["-i", str(voice)]
        filters.append(f"[{n}:a]aresample=48000,aformat=channel_layouts=stereo[v]")
        labels.append("[v]")
        n += 1
    for i, c in enumerate(used):
        inputs += ["-i", c.file]
        length = c.end - c.start
        delay = int(c.start * 1000)
        filters.append(
            f"[{n}:a]atrim=start={c.offset:.3f}:duration={length:.3f},asetpts=PTS-STARTPTS,"
            f"aresample=48000,aformat=channel_layouts=stereo,"
            f"afade=t=in:d={c.fade_s},afade=t=out:st={max(0.0, length - c.fade_s):.3f}:d={c.fade_s},"
            f"volume={c.gain_db}dB,adelay={delay}|{delay}[m{i}]")
        labels.append(f"[m{i}]")
        n += 1
    filters.append(
        f"{''.join(labels)}amix=inputs={len(labels)}:duration=first:normalize=0,"
        f"afade=t=out:st={max(0.0, duration - fade_out_s):.3f}:d={fade_out_s}[out]")
    out_wav.parent.mkdir(parents=True, exist_ok=True)
    cmd = [ffmpeg, "-y", "-loglevel", "error", *inputs, "-filter_complex", ";".join(filters),
           "-map", "[out]", "-t", f"{duration:.3f}", "-ar", "48000", str(out_wav)]
    subprocess.run(cmd, check=True)
    return out_wav, used, missing
