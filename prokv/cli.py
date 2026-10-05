"""Turn text into an editorial infographic Reel (vertical 1080×1920 MP4).

Examples:
    python -m prokv --file examples/demo_ru.txt            # -> output/video.mp4
    python -m prokv "Ваш текст или тема ролика..."
    cat text.txt | python -m prokv --file -
    python -m prokv --from-plan output/storyboard.json     # re-render an edited storyboard
    python -m prokv --map examples/maps/001_billie_jean.json  # "Карта одного трека" episode
    python -m prokv --map ep.json --voiceover-file voice.txt    # + Silero voice track
    python -m prokv --file text.txt --voice voiceover/my.wav    # + an existing voice track
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from prokv.config import VideoSpec
from prokv.export import load_storyboard, save_storyboard
from prokv.pipeline import STORYBOARD_NAME, VIDEO_NAME, Pipeline
from prokv.style import DEFAULT_STYLE, load_style


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="prokv", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("text", nargs="?", help="The text (or topic) of the video")
    parser.add_argument("--file", "-f", help="Read the text from a file ('-' for stdin)")
    parser.add_argument("--from-plan", type=Path, metavar="STORYBOARD", help="Render an existing storyboard.json")
    parser.add_argument("--out", "-o", type=Path, help="Output folder (default: output/)")
    parser.add_argument("--style", type=Path, help="JSON file with style overrides (see examples/style_override.json)")
    parser.add_argument("--max-scenes", type=int, default=12, help="Upper limit on the number of scenes")
    parser.add_argument("--fps", type=int, default=30, help="Frames per second (default 30)")
    parser.add_argument("--map", type=Path, metavar="EPISODE", help="Render a one-track map episode (JSON)")
    parser.add_argument("--voice", type=Path, metavar="WAV", help="Use this audio file as the voice track")
    parser.add_argument("--voiceover", metavar="TEXT", help="Russian text to speak (Silero TTS) as the voice track")
    parser.add_argument("--voiceover-file", metavar="TXT", help="Read the voiceover text from a file")
    parser.add_argument("--speaker", help="Silero voice for --voiceover (aidar, eugene, baya, kseniya, xenia)")
    parser.add_argument("--plan-only", action="store_true", help="Only write storyboard.json, no video")
    args = parser.parse_args(argv)

    style = load_style(args.style) if args.style else DEFAULT_STYLE
    audio = _voice_track(args) if not args.plan_only else None
    pipeline = Pipeline(style=style, spec=VideoSpec(fps=args.fps), max_scenes=args.max_scenes)
    started = time.monotonic()

    if args.map:
        result = render_track_map(args.map, (args.out or Path("output")) / f"{args.map.stem}.mp4", style,
                                  VideoSpec(fps=args.fps), audio)
    elif args.from_plan:
        storyboard = load_storyboard(args.from_plan)
        out = (args.out or args.from_plan.parent) / VIDEO_NAME
        result = pipeline.render(storyboard, out, audio)
    else:
        if args.file:
            text = sys.stdin.read() if args.file == "-" else Path(args.file).read_text(encoding="utf-8")
        elif args.text:
            text = args.text
        else:
            parser.error("give the text as an argument, or use --file / --from-plan")
        out_dir = args.out or Path("output")
        storyboard = pipeline.plan(text)
        _print_plan(storyboard)
        save_storyboard(storyboard, out_dir / STORYBOARD_NAME)
        result = out_dir / STORYBOARD_NAME if args.plan_only else pipeline.render(storyboard, out_dir / VIDEO_NAME, audio)
    print(f"Wrote {result}  ({time.monotonic() - started:.0f}s)")
    return 0


def _voice_track(args) -> Path | None:
    """--voice FILE, or synthesise --voiceover / --voiceover-file with Silero TTS."""
    if args.voice:
        return args.voice
    text = Path(args.voiceover_file).read_text(encoding="utf-8") if args.voiceover_file else args.voiceover
    if not text:
        return None
    from prokv.voice import SileroTTS, VoiceConfig, wav_duration

    config = VoiceConfig(speaker=args.speaker) if args.speaker else VoiceConfig()
    path = SileroTTS(config).synthesize(text)
    print(f"Voiceover: {path} ({wav_duration(path):.1f}s, voice {config.speaker})")
    return path


def render_track_map(path: Path, out_path: Path, style, spec: VideoSpec, audio: Path | None = None) -> Path:
    from prokv.content.track_map import Episode
    from prokv.export import encode_mp4
    from prokv.layout.maps import build_episode
    from prokv.render.stage_renderer import StageRenderer

    ep = Episode.load(path)
    stage, overlay = build_episode(ep, style, spec)
    renderer = StageRenderer(stage, spec.fps, style.grain, overlay)
    print(f"№{ep.number:03d} {ep.track} — {stage.duration:.1f}s, {len(ep.sections)} sections, "
          f"{len(stage.nodes)} nodes, {len(stage.links)} links")
    for sec in ep.sections:
        print(f"  {sec.start:5.1f}–{sec.end:5.1f}  {sec.type}")
    if audio:
        from prokv.voice import wav_duration
        if audio.suffix.lower() == ".wav" and wav_duration(audio) > stage.duration + 0.05:
            print(f"Warning: the voice track ({wav_duration(audio):.1f}s) is longer than the video "
                  f"({stage.duration:.1f}s) and will be cut.")
    return encode_mp4(renderer.frames(), spec, out_path, audio=audio)


def _print_plan(storyboard) -> None:
    print(f"«{storyboard.title}» — {len(storyboard.scenes)} scenes, {storyboard.duration_s:.1f}s")
    for i, scene in enumerate(storyboard.scenes, 1):
        c = scene.content
        summary = c.number or c.headline or c.quote or " / ".join(c.items[:2] or [p[1] for p in c.pairs])
        print(f"  {i:02d}  {scene.kind:<11} {scene.duration_s:>4.1f}s  {summary}")
