#!/usr/bin/env bash
# Prok-V: set up local Silero TTS on macOS (Intel or Apple Silicon) and test the
# whole chain  text → Silero → WAV → FFmpeg → MP4 with a voice track.
#
#   cd /path/to/Prok-V && bash scripts/setup_mac.sh
#
# Safe by design: no sudo, nothing removed, system Python untouched. Everything
# goes into Homebrew packages (python@3.12, ffmpeg) and the project's .venv.
set -euo pipefail
cd "$(dirname "$0")/.."

step() { printf '\n\033[1m== %s\033[0m\n' "$*"; }
stop() { printf '\n\033[31mSTOP:\033[0m %s\n' "$*"; exit 1; }

step "1. System"
[[ "$(uname -s)" == "Darwin" ]] || stop "This script is for macOS."
ARCH="$(uname -m)"; MACOS="$(sw_vers -productVersion)"
echo "macOS $MACOS, CPU $ARCH"
for py in python3.10 python3.11 python3.12 python3.13 python3; do
  command -v "$py" >/dev/null && echo "  found $py: $("$py" --version 2>&1) ($(command -v "$py"))"
done

# PyTorch: Intel Macs stop at 2.2.2 (Python ≤ 3.12); Apple Silicon gets current builds.
if [[ "$ARCH" == "x86_64" ]]; then TORCH_SPEC="torch==2.2.2"; EXTRA_SPEC="numpy<2"
else TORCH_SPEC="torch>=2.0"; EXTRA_SPEC=""; fi

step "2. Homebrew"
if ! command -v brew >/dev/null; then
  stop "Homebrew is not installed. Install it yourself (it asks for your password):
  /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"
then run this script again."
fi
echo "brew $(brew --version | head -1)"

step "3. Python 3.12 (compatible with PyTorch on every Mac)"
PY=""
for cand in python3.12 python3.11 python3.10; do
  if command -v "$cand" >/dev/null; then PY="$(command -v "$cand")"; break; fi
done
if [[ -z "$PY" ]]; then
  brew install python@3.12
  PY="$(brew --prefix python@3.12)/bin/python3.12"
fi
echo "Using $PY ($("$PY" --version))"

step "4. FFmpeg"
command -v ffmpeg >/dev/null || brew install ffmpeg
ffmpeg -version | head -1

step "5. Virtual environment .venv"
[[ -d .venv ]] || "$PY" -m venv .venv
# shellcheck disable=SC1091
source .venv/bin/activate
python -m pip install -q --upgrade pip
echo "venv Python: $(python --version)"

step "6. Prok-V + PyTorch ($TORCH_SPEC)"
python -m pip install -q $TORCH_SPEC $EXTRA_SPEC
python -m pip install -q -e .
python -c "import torch, PIL; print('torch', torch.__version__, '| Pillow', PIL.__version__)"

step "7. Check"
python -m prokv.voice --check || true

step "8. Silero model + test voiceover"
TEXT="Привет! Это тестовая озвучка проекта Prok-V."
mkdir -p voiceover
if ! python -m prokv.voice "$TEXT" --out voiceover/test_ru.wav; then
  echo "Model v5_5_ru did not load with this PyTorch — falling back to v4_ru."
  export PROKV_SILERO_MODEL=v4_ru
  python -m prokv.voice "$TEXT" --out voiceover/test_ru.wav
fi

step "9. Is the WAV real?"
afinfo voiceover/test_ru.wav | grep -E "File type|Data format|estimated duration" || true
python - <<'PY'
import wave, array
with wave.open("voiceover/test_ru.wav") as f:
    n, rate = f.getnframes(), f.getframerate()
    pcm = array.array("h", f.readframes(n))
peak = max(abs(x) for x in pcm) if pcm else 0
print(f"{n / rate:.1f} s, {rate} Hz, peak {peak}")
assert n / rate > 1.0 and peak > 1000, "the file is empty or silent"
print("OK: speech audio present")
PY
echo "Playing it now (you should hear the voice)…"
afplay voiceover/test_ru.wav || echo "afplay failed — open voiceover/test_ru.wav in QuickTime to listen."

step "10. Full pipeline: text → Silero → WAV → FFmpeg → MP4"
python -m prokv "Выручка выросла на 35% за год. Итог: это работает." \
  --voiceover "$TEXT" --out output/voice_test
ffprobe -v error -show_entries stream=codec_type,codec_name:format=duration -of compact output/voice_test/video.mp4
ffprobe -v error -select_streams a -show_entries stream=codec_name -of csv=p=0 output/voice_test/video.mp4 \
  | grep -q aac && echo "OK: MP4 has a voice track (AAC)" || stop "no audio stream in the MP4"

step "Done"
echo "Python:   $(python --version)  (.venv)"
echo "PyTorch:  $(python -c 'import torch; print(torch.__version__)')"
echo "FFmpeg:   $(ffmpeg -version | head -1 | cut -d' ' -f3)"
echo "Model:    $(ls models/silero/*.pt)"
echo "WAV:      voiceover/  (test: voiceover/test_ru.wav)"
echo "MP4:      output/voice_test/video.mp4"
echo "Later:    source .venv/bin/activate  before using prokv"
