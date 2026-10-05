import json
import math
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from prokv.voice import SileroTTS, VoiceConfig, wav_duration
from prokv.voice.silero import split_text, write_wav


class FakeSilero:
    """Stands in for the Silero model: 0.5 s of a quiet tone per call."""

    def __init__(self):
        self.calls = []

    def apply_tts(self, text, speaker, sample_rate):
        self.calls.append((text, speaker, sample_rate))
        n = sample_rate // 2
        return [0.2 * math.sin(2 * math.pi * 220 * i / sample_rate) for i in range(n)]


class VoiceModuleTest(unittest.TestCase):
    def test_synthesize_writes_wav_to_voiceover_folder(self):
        with tempfile.TemporaryDirectory() as tmp:
            fake = FakeSilero()
            config = VoiceConfig(speaker="baya", sample_rate=24000, output_dir=Path(tmp) / "voiceover")
            path = SileroTTS(config, model=fake).synthesize("Привет! Это проверка озвучки.")
            self.assertEqual(path.parent, config.output_dir)
            self.assertTrue(path.name.endswith("_baya.wav"))
            self.assertAlmostEqual(wav_duration(path), 0.5, places=2)
            self.assertEqual(fake.calls, [("Привет! Это проверка озвучки.", "baya", 24000)])

    def test_long_text_is_split_with_pauses(self):
        text = " ".join(f"Предложение номер {'раз' * 20} {i}." for i in range(40))
        chunks = split_text(text, 300)
        self.assertTrue(all(len(c) <= 300 for c in chunks))
        self.assertEqual(" ".join(chunks), " ".join(text.split()))
        with tempfile.TemporaryDirectory() as tmp:
            fake = FakeSilero()
            cfg = VoiceConfig(sample_rate=8000, pause_s=0.25)
            path = SileroTTS(cfg, model=fake).synthesize("Один. " * 300, Path(tmp) / "long.wav")
            n = len(fake.calls)
            self.assertGreater(n, 1)
            self.assertAlmostEqual(wav_duration(path), n * 0.5 + (n - 1) * 0.25, places=2)

    def test_voice_and_sample_rate_are_validated(self):
        with self.assertRaises(ValueError):
            SileroTTS(VoiceConfig(speaker="nobody"))
        with self.assertRaises(ValueError):
            SileroTTS(VoiceConfig(sample_rate=44100))

    @unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "FFmpeg not installed")
    def test_voice_track_is_muxed_into_mp4(self):
        from PIL import Image

        from prokv.config import VideoSpec
        from prokv.export import encode_mp4

        with tempfile.TemporaryDirectory() as tmp:
            wav = write_wav(Path(tmp) / "voice.wav", [0.1] * 48000, 48000)  # 1 s of audio
            spec = VideoSpec(fps=10)
            frames = (Image.new("RGB", (1080, 1920), "#E8DDC8") for _ in range(20))  # 2 s of video
            video = encode_mp4(frames, spec, Path(tmp) / "out.mp4", audio=wav)
            probe = json.loads(subprocess.run(
                ["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,codec_name:format=duration",
                 "-of", "json", str(video)], capture_output=True, text=True, check=True).stdout)
            codecs = {s["codec_type"]: s["codec_name"] for s in probe["streams"]}
            self.assertEqual(codecs, {"video": "h264", "audio": "aac"})
            self.assertAlmostEqual(float(probe["format"]["duration"]), 2.0, delta=0.1)


@unittest.skipUnless(os.environ.get("PROKV_SILERO_TEST") == "1",
                     "real Silero test: set PROKV_SILERO_TEST=1 (needs PyTorch; downloads the model once)")
class RealSileroTest(unittest.TestCase):
    def test_real_russian_speech(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = SileroTTS().synthesize("Привет! Это проверка локальной озвучки.", Path(tmp) / "ru.wav")
            self.assertGreater(wav_duration(path), 1.0)


if __name__ == "__main__":
    unittest.main()
