"""Command-line entry point: `python -m prokv "a prompt" --caption "Hello"`."""

from __future__ import annotations

import argparse
from pathlib import Path

from prokv.config import VideoSpec
from prokv.pipeline import Pipeline


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="prokv", description=__doc__)
    parser.add_argument("prompt", help="Text prompt describing the visuals")
    parser.add_argument("--caption", action="append", default=[], help="Caption text (repeatable)")
    parser.add_argument("--images", type=int, default=4, help="Number of images to generate")
    parser.add_argument("--duration", type=float, default=10.0, help="Video length in seconds")
    parser.add_argument("--out", type=Path, default=Path("output"), help="Output directory")
    args = parser.parse_args(argv)

    pipeline = Pipeline(spec=VideoSpec(duration_s=args.duration))
    result = pipeline.run(args.prompt, args.caption, args.out, args.images)
    print(f"Wrote {result}")
    return 0
