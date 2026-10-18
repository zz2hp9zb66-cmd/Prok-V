"""Bridge to the Remotion renderer and FFmpeg checks."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

from .project import ProjectDir

RENDERER = Path(__file__).resolve().parent.parent / "renderer"


def write_props(pd: ProjectDir, stepped: bool = True) -> Path:
    project = pd.project()
    data = {
        "project": project.model_dump(mode="json"),
        "scenes": [s.model_dump(mode="json") for s in pd.scenes()],
        "timeline": pd.timeline().model_dump(mode="json"),
        "stepped": stepped,
    }
    path = pd.abs("renders/props.json")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    return path


def _run(pd: ProjectDir, *extra: str) -> None:
    props = write_props(pd)
    cmd = ["node", "scripts/render.mjs", "--project", str(pd.root), "--props", str(props), *extra]
    subprocess.run(cmd, cwd=RENDERER, check=True)


def stills(pd: ProjectDir, scene_ids: list[str] | None = None) -> list[Path]:
    out = pd.abs("previews")
    extra = ["--stills", str(out)]
    if scene_ids:
        extra += ["--scenes", ",".join(scene_ids)]
    _run(pd, *extra)
    return [out / f"scene_{s}.png" for s in (scene_ids or pd.scene_ids())]


def video(pd: ProjectDir, output: Path) -> Path:
    output.parent.mkdir(parents=True, exist_ok=True)
    _run(pd, "--video", str(output))
    return output


def scene_video(pd: ProjectDir, scene_id: str) -> Path:
    output = pd.abs(f"renders/scenes/scene_{scene_id}.mp4")
    output.parent.mkdir(parents=True, exist_ok=True)
    _run(pd, "--scene-video", scene_id, str(output))
    return output


def probe(path: Path) -> dict:
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,codec_name,width,height,r_frame_rate,pix_fmt:format=duration",
         "-of", "json", str(path)],
        check=True, capture_output=True, text=True,
    ).stdout
    return json.loads(out)


def check_spec(info: dict, width: int, height: int, fps: int) -> list[str]:
    """Return a list of deviations from the delivery spec (empty = OK)."""
    problems = []
    streams = info.get("streams", [])
    videos = [s for s in streams if s["codec_type"] == "video"]
    if any(s["codec_type"] == "audio" for s in streams):
        problems.append("has an audio stream")
    if len(videos) != 1:
        return problems + [f"expected 1 video stream, got {len(videos)}"]
    v = videos[0]
    if (v["width"], v["height"]) != (width, height):
        problems.append(f"size {v['width']}x{v['height']}")
    if v["r_frame_rate"] != f"{fps}/1":
        problems.append(f"fps {v['r_frame_rate']}")
    if v["codec_name"] != "h264" or v["pix_fmt"] != "yuv420p":
        problems.append(f"codec {v['codec_name']}/{v['pix_fmt']}")
    return problems
