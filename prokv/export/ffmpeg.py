"""Encode frames to H.264 MP4 with FFmpeg (raw RGB frames piped via stdin)."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Iterable

from PIL import Image

from prokv.config import VideoSpec


def ffmpeg_available(binary: str = "ffmpeg") -> bool:
    return shutil.which(binary) is not None


def encode_mp4(frames: Iterable[Image.Image], spec: VideoSpec, out_path: Path, crf: int = 18,
               preset: str = "medium", binary: str = "ffmpeg", audio: Path | None = None) -> Path:
    """Encode frames to H.264. With `audio`, it becomes the AAC voice track: padded with
    silence if shorter than the video, cut if longer (the video length always wins)."""
    ffmpeg = shutil.which(binary)
    if ffmpeg is None:
        raise RuntimeError(
            f"FFmpeg not found ({binary!r}). Install it (macOS: brew install ffmpeg, "
            "Ubuntu: sudo apt install ffmpeg, Windows: winget install ffmpeg) and make sure it is on PATH."
        )
    if audio is not None and not Path(audio).is_file():
        raise FileNotFoundError(f"Voice track not found: {audio}")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        ffmpeg, "-y", "-loglevel", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{spec.width}x{spec.height}", "-r", str(spec.fps),
        "-i", "-",
        *(["-i", str(audio), "-map", "0:v", "-map", "1:a", "-c:a", "aac", "-b:a", "192k",
           "-af", "apad", "-shortest"] if audio else []),
        "-c:v", "libx264", "-preset", preset, "-crf", str(crf), "-tune", "stillimage",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart",
        str(out_path),
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        for frame in frames:
            proc.stdin.write(frame.convert("RGB").tobytes())
        proc.stdin.close()
    except BrokenPipeError:
        pass  # FFmpeg exited early; its error is reported below.
    finally:
        stderr = proc.stderr.read().decode(errors="replace")
        proc.stderr.close()
        proc.wait()
    if proc.returncode != 0:
        raise RuntimeError(f"FFmpeg failed (exit {proc.returncode}): {stderr.strip()}")
    return out_path
