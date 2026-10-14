"""Silero TTS, run locally on CPU: Russian text in, WAV file out.

Uses the official standalone loading method (torch.package): the model file is
downloaded once from models.silero.ai into models/silero/ and then works
offline. The only extra dependency is PyTorch (pip install -e ".[tts]").

Model licence: Silero's Russian v5 models are CC BY-NC (non-commercial);
check https://github.com/snakers4/silero-models before commercial use.
"""

from __future__ import annotations

import os
import re
import wave
from array import array
from dataclasses import dataclass, replace
from pathlib import Path

MODEL_URL = "https://models.silero.ai/models/tts/ru/{model}.pt"
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Russian speakers of the v5 models.
VOICES = {
    "aidar": "мужской",
    "eugene": "мужской",
    "baya": "женский",
    "kseniya": "женский",
    "xenia": "женский",
}
DEFAULT_VOICE = "aidar"
SAMPLE_RATES = (8000, 24000, 48000)
MAX_CHUNK_CHARS = 800   # Silero handles long input poorly; text is synthesised sentence by sentence


@dataclass(frozen=True)
class VoiceConfig:
    """Everything that defines the voice. Change `speaker` to switch voices."""

    speaker: str = DEFAULT_VOICE
    model: str = os.environ.get("PROKV_SILERO_MODEL", "v5_5_ru")  # e.g. v4_ru for old PyTorch
    sample_rate: int = 48000
    pause_s: float = 0.35                      # silence between sentence chunks
    models_dir: Path = PROJECT_ROOT / "models" / "silero"
    output_dir: Path = PROJECT_ROOT / "voiceover"
    threads: int = 4

    def with_(self, **kwargs) -> "VoiceConfig":
        return replace(self, **kwargs)

    def validate(self) -> None:
        if self.speaker not in VOICES:
            raise ValueError(f"Unknown voice {self.speaker!r}. Available: {', '.join(VOICES)}")
        if self.sample_rate not in SAMPLE_RATES:
            raise ValueError(f"sample_rate must be one of {SAMPLE_RATES}")


class SileroTTS:
    """`SileroTTS().synthesize("Привет!")` -> voiceover/<name>.wav"""

    def __init__(self, config: VoiceConfig = VoiceConfig(), model=None) -> None:
        config.validate()
        self.config = config
        self._model = model        # injected in tests; loaded lazily otherwise

    # -- model ---------------------------------------------------------------

    @property
    def model_path(self) -> Path:
        return self.config.models_dir / f"{self.config.model}.pt"

    def load(self):
        if self._model is not None:
            return self._model
        try:
            import torch
        except ImportError as error:
            raise RuntimeError('PyTorch is not installed. Run: pip install -e ".[tts]"') from error
        if not self.model_path.exists():
            self.model_path.parent.mkdir(parents=True, exist_ok=True)
            url = MODEL_URL.format(model=self.config.model)
            print(f"Downloading Silero model {self.config.model} (once) -> {self.model_path}")
            torch.hub.download_url_to_file(url, str(self.model_path))
        torch.set_num_threads(self.config.threads)
        model = torch.package.PackageImporter(str(self.model_path)).load_pickle("tts_models", "model")
        model.to(torch.device("cpu"))
        self._model = model
        return model

    # -- synthesis -----------------------------------------------------------

    def speak(self, text: str) -> list[float]:
        """Samples of `text` spoken sentence by sentence, with a short pause between sentences."""
        text = " ".join(text.split())
        if not text:
            raise ValueError("The text is empty")
        if re.search(r"\d", text):
            print("Warning: Silero may skip digits — write numbers in words (e.g. «тысяча девятьсот "
                  "восемьдесят второй») for reliable reading.")
        if re.search(r"[A-Za-z]", text):
            print("Warning: the Russian model skips Latin letters — write names in Cyrillic "
                  "(e.g. «Прок-Ви» instead of «Prok-V»).")
        model = self.load()
        cfg = self.config
        silence = [0.0] * int(cfg.pause_s * cfg.sample_rate)
        samples: list[float] = []
        chunks = [c for sentence in re.split(r"(?<=[.!?…])\s+", text) for c in split_text(sentence)]
        for i, chunk in enumerate(chunks):
            audio = model.apply_tts(text=chunk, speaker=cfg.speaker, sample_rate=cfg.sample_rate)
            if i:
                samples.extend(silence)
            samples.extend(audio.tolist() if hasattr(audio, "tolist") else list(audio))
        return samples

    def synthesize(self, text: str, out_path: Path | str | None = None) -> Path:
        """Speak `text` and write a mono 16-bit WAV. Returns the file path."""
        samples = self.speak(text)
        cfg = self.config
        path = Path(out_path) if out_path else cfg.output_dir / f"{slug(text)}_{cfg.speaker}.wav"
        write_wav(path, samples, cfg.sample_rate)
        return path


def split_text(text: str, limit: int = MAX_CHUNK_CHARS) -> list[str]:
    """Split into chunks of whole sentences no longer than `limit` characters."""
    sentences = re.split(r"(?<=[.!?…])\s+", text)
    chunks, current = [], ""
    for sentence in sentences:
        while len(sentence) > limit:  # a single overlong sentence: cut at a comma or space
            cut = max(sentence.rfind(",", 0, limit), sentence.rfind(" ", 0, limit))
            cut = cut if cut > 0 else limit
            chunks.append(sentence[:cut + 1].strip())
            sentence = sentence[cut + 1:].strip()
        if current and len(current) + 1 + len(sentence) > limit:
            chunks.append(current)
            current = sentence
        else:
            current = f"{current} {sentence}".strip()
    if current:
        chunks.append(current)
    return [c for c in chunks if c]


def write_wav(path: Path, samples, sample_rate: int) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    pcm = array("h", (int(max(-1.0, min(1.0, s)) * 32767) for s in samples))
    with wave.open(str(path), "wb") as f:
        f.setnchannels(1)
        f.setsampwidth(2)
        f.setframerate(sample_rate)
        f.writeframes(pcm.tobytes())
    return path


def wav_duration(path: Path | str) -> float:
    with wave.open(str(path), "rb") as f:
        return f.getnframes() / f.getframerate()


_TRANSLIT = str.maketrans("абвгдеёжзийклмнопрстуфхцчшщъыьэюя",
                          "abvgdeezziyklmnoprstufhccss_y_eua")


def slug(text: str, words: int = 5) -> str:
    base = "_".join(re.findall(r"\w+", text.lower())[:words]).translate(_TRANSLIT)
    return re.sub(r"[^a-z0-9_]", "", base)[:60] or "voiceover"
