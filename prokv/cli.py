"""Command-line entry point.

    python -m prokv "a prompt" --caption "Hello" --caption "World"   # -> output/video.mp4
    python -m prokv --from-plan output/render_plan.json               # re-render an existing plan
"""

from __future__ import annotations

import argparse
from dataclasses import replace
from pathlib import Path

from prokv.config import VideoSpec
from prokv.export import VIDEO_NAME, RenderPlanExporter, VideoExporter, load_render_plan
from prokv.pipeline import Pipeline
from prokv.style import DEFAULT_STYLE


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="prokv", description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("prompt", nargs="?", help="Text prompt describing the visuals")
    parser.add_argument("--caption", action="append", default=[], help="Caption text (repeatable)")
    parser.add_argument("--images", type=int, default=4, help="Number of images to generate")
    parser.add_argument("--duration", type=float, default=10.0, help="Video length in seconds")
    parser.add_argument("--fps", type=int, default=30, help="Frames per second")
    parser.add_argument("--out", type=Path, help="Output directory (default: output/, or the plan's folder)")
    parser.add_argument("--font", help="Path to a .ttf/.otf font for captions")
    parser.add_argument("--plan-only", action="store_true", help="Write render_plan.json without a video")
    parser.add_argument("--from-plan", type=Path, metavar="PLAN", help="Render an existing render_plan.json")
    args = parser.parse_args(argv)

    style = DEFAULT_STYLE
    if args.font:
        style = replace(style, caption=replace(style.caption, font_path=args.font))
    video_exporter = VideoExporter(style=style)

    if args.from_plan:
        out_path = (args.out or args.from_plan.parent) / VIDEO_NAME
        result = video_exporter.render(load_render_plan(args.from_plan), out_path)
    else:
        if not args.prompt:
            parser.error("a prompt is required unless --from-plan is given")
        pipeline = Pipeline(
            exporter=RenderPlanExporter() if args.plan_only else video_exporter,
            spec=VideoSpec(fps=args.fps, duration_s=args.duration),
            style=style,
        )
        result = pipeline.run(args.prompt, args.caption, args.out or Path("output"), args.images)
    print(f"Wrote {result}")
    return 0
