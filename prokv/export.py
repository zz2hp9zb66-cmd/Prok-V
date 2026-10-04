"""Stage 5: export the project as a 9:16 video."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from abc import ABC, abstractmethod
from dataclasses import asdict
from pathlib import Path

from prokv.models import Project, project_from_dict
from prokv.rendering import FrameRenderer
from prokv.style import DEFAULT_STYLE, VisualStyle

PLAN_NAME = "render_plan.json"
VIDEO_NAME = "video.mp4"


class Exporter(ABC):
    """Writes the final output for a project and returns its path."""

    @abstractmethod
    def export(self, project: Project, out_dir: Path) -> Path:
        ...


class RenderPlanExporter(Exporter):
    """Writes a JSON render plan describing the full video.

    The plan contains everything a renderer needs (canvas, layers, keyframes,
    captions) to draw each frame. Image paths are stored relative to the plan.
    """

    def export(self, project: Project, out_dir: Path) -> Path:
        out_dir.mkdir(parents=True, exist_ok=True)
        data = asdict(project)
        for layer in data["composition"]["layers"]:
            path = Path(layer["image"]["path"])
            layer["image"]["path"] = Path(os.path.relpath(path.resolve(), out_dir.resolve())).as_posix()
        path = out_dir / PLAN_NAME
        path.write_text(json.dumps(data, indent=2, ensure_ascii=False, default=str))
        return path


def load_render_plan(path: Path) -> Project:
    """Read a render_plan.json written by RenderPlanExporter."""
    return project_from_dict(json.loads(path.read_text()), base_dir=path.parent)


class VideoExporter(Exporter):
    """Renders frames with Pillow and encodes them to H.264 MP4 with FFmpeg.

    Also writes the render plan next to the video so it can be re-rendered later.
    """

    def __init__(
        self,
        style: VisualStyle = DEFAULT_STYLE,
        crf: int = 20,
        preset: str = "medium",
        ffmpeg: str = "ffmpeg",
    ) -> None:
        self.style = style
        self.crf = crf
        self.preset = preset
        self.ffmpeg = ffmpeg

    def export(self, project: Project, out_dir: Path) -> Path:
        RenderPlanExporter().export(project, out_dir)
        return self.render(project, out_dir / VIDEO_NAME)

    def render(self, project: Project, out_path: Path) -> Path:
        ffmpeg = shutil.which(self.ffmpeg)
        if ffmpeg is None:
            raise RuntimeError(f"FFmpeg not found ({self.ffmpeg!r}). Install it and make sure it is on PATH.")
        spec = project.spec
        renderer = FrameRenderer(project, self.style)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        cmd = [
            ffmpeg, "-y", "-loglevel", "error",
            "-f", "rawvideo", "-pix_fmt", "rgb24",
            "-s", f"{spec.width}x{spec.height}", "-r", str(spec.fps), "-i", "-",
            "-c:v", "libx264", "-preset", self.preset, "-crf", str(self.crf),
            "-pix_fmt", "yuv420p", "-movflags", "+faststart",
            str(out_path),
        ]
        frame_count = max(1, round(spec.duration_s * spec.fps))
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            for i in range(frame_count):
                proc.stdin.write(renderer.render(i / spec.fps).tobytes())
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
