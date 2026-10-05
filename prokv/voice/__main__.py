"""Silero TTS from the command line.

    python -m prokv.voice "Текст для озвучки"              # -> voiceover/<name>.wav
    python -m prokv.voice --file text.txt --speaker baya
    python -m prokv.voice --test                           # short Russian test file
    python -m prokv.voice --samples                        # one sample per voice, to choose by ear
    python -m prokv.voice --check                          # is this computer ready?
"""

from __future__ import annotations

import argparse
import platform
import shutil
import sys
import time
from pathlib import Path

from prokv.voice.silero import DEFAULT_VOICE, VOICES, SileroTTS, VoiceConfig, wav_duration

TEST_TEXT = "Привет! Это проверка локальной озвучки Prok-V. Голос создаётся прямо на вашем компьютере."
SAMPLE_TEXT = "Карта одного трека. Сегодня разбираем, кто на самом деле создал этот звук."


def check() -> int:
    ok = True
    print(f"Python   {sys.version.split()[0]}  ({platform.system()} {platform.machine()}, {platform.mac_ver()[0] or ''})")
    if sys.version_info < (3, 10):
        print("  ✗ Python 3.10+ is required"); ok = False
    try:
        import torch
        major, minor = (int(x) for x in torch.__version__.split(".")[:2])
        print(f"PyTorch  {torch.__version__}" + ("" if (major, minor) >= (2, 0) else "  ✗ 2.0+ required"))
        ok &= (major, minor) >= (2, 0)
        print(f"         torch.package: {'yes' if hasattr(torch, 'package') else 'no ✗'}")
    except ImportError:
        print('PyTorch  not installed ✗  ->  pip install -e ".[tts]"'); ok = False
        if platform.system() == "Darwin" and platform.machine() == "x86_64" and sys.version_info >= (3, 13):
            print("  Intel Mac: PyTorch exists only for Python ≤ 3.12 — use Python 3.12.")
    model = VoiceConfig().models_dir / f"{VoiceConfig().model}.pt"
    print(f"Model    {'cached: ' + str(model) if model.exists() else 'not downloaded yet (downloads on first use, internet needed once)'}")
    print(f"FFmpeg   {shutil.which('ffmpeg') or 'not found ✗'}")
    print("Ready." if ok else "Not ready — see ✗ above.")
    return 0 if ok else 1


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="python -m prokv.voice", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("text", nargs="?", help="Russian text to speak")
    parser.add_argument("--file", "-f", help="Read the text from a file")
    parser.add_argument("--speaker", default=DEFAULT_VOICE, choices=sorted(VOICES),
                        help=f"Voice (default {DEFAULT_VOICE})")
    parser.add_argument("--out", "-o", type=Path, help="Output WAV path (default: voiceover/<name>.wav)")
    parser.add_argument("--test", action="store_true", help="Create voiceover/test_ru.wav")
    parser.add_argument("--samples", action="store_true", help="Create one sample per voice")
    parser.add_argument("--check", action="store_true", help="Check Python, PyTorch, model and FFmpeg")
    args = parser.parse_args(argv)

    if args.check:
        return check()
    config = VoiceConfig(speaker=args.speaker)
    if args.samples:
        for name, kind in VOICES.items():
            tts = SileroTTS(config.with_(speaker=name))
            path = tts.synthesize(SAMPLE_TEXT, config.output_dir / f"sample_{name}.wav")
            print(f"{name:<8} {kind:<8} {wav_duration(path):4.1f}s  {path}")
        return 0
    if args.test:
        text, out = TEST_TEXT, args.out or config.output_dir / "test_ru.wav"
    else:
        text = Path(args.file).read_text(encoding="utf-8") if args.file else args.text
        if not text:
            parser.error("give the text, --file, --test, --samples or --check")
        out = args.out
    started = time.monotonic()
    path = SileroTTS(config).synthesize(text, out)
    print(f"Wrote {path}  ({wav_duration(path):.1f}s of speech, voice {config.speaker}, "
          f"{time.monotonic() - started:.1f}s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
