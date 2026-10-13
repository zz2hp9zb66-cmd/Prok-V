import json
import math
import shutil
import subprocess
import tempfile
import unittest
import wave
from pathlib import Path

from prokv.content.documentary import Documentary
from prokv.layout.documentary import VISUALS, build_documentary
from prokv.render.stage_renderer import StageRenderer
from prokv.voice import SileroTTS, VoiceConfig, wav_duration
from prokv.voice.documentary import build_voice_track

SCENARIO = Path(__file__).resolve().parent.parent / "examples" / "documentary" / "music_1990_2000.json"


class FakeSilero:
    """~14.5 characters per second, like Silero's Russian pace."""

    def apply_tts(self, text, speaker, sample_rate):
        n = int(len(text) / 14.5 * sample_rate)
        return [0.2 * math.sin(2 * math.pi * 200 * i / sample_rate) for i in range(n)]


def _peak(path: Path, start: float, end: float) -> int:
    with wave.open(str(path)) as f:
        rate, width, channels = f.getframerate(), f.getsampwidth(), f.getnchannels()
        f.setpos(int(start * rate))
        data = f.readframes(int((end - start) * rate))
    import array
    samples = array.array("h" if width == 2 else "i", data)
    return max((abs(s) for s in samples), default=0)


class DocumentaryTest(unittest.TestCase):
    def test_scenario_is_valid(self):
        doc = Documentary.load(SCENARIO)
        self.assertEqual(doc.duration, 95.0)
        self.assertEqual(len(doc.scenes), 10)
        self.assertEqual({s.visual["type"] for s in doc.scenes}, set(VISUALS))
        for sc in doc.scenes:
            self.assertTrue(2.0 <= sc.card_s <= 4.0)
            for card in sc.cards:
                self.assertTrue(card.artist and card.track and card.year)

    def test_every_scene_renders(self):
        doc = Documentary.load(SCENARIO)
        stage, overlay = build_documentary(doc)
        renderer = StageRenderer(stage, 30, 4, overlay)
        self.assertEqual(renderer.frame_count, 95 * 30)
        frames = [renderer.render(sc.start + sc.length * 0.65) for sc in doc.scenes]
        self.assertEqual(len({f.tobytes() for f in frames}), len(frames))
        self.assertTrue(all(f.size == (1080, 1920) for f in frames))

    def test_voice_track_follows_the_timeline(self):
        doc = Documentary.load(SCENARIO)
        with tempfile.TemporaryDirectory() as tmp:
            tts = SileroTTS(VoiceConfig(speaker="eugene", sample_rate=8000), model=FakeSilero())
            track = build_voice_track(doc, Path(tmp), tts=tts)
            self.assertAlmostEqual(wav_duration(track.wav), doc.duration, places=1)
            prev_end = 0.0
            for seg, sc in zip(track.segments, doc.scenes):
                self.assertGreaterEqual(seg.start, sc.start)                 # never before its scene
                self.assertGreaterEqual(seg.start, prev_end)                 # never overlapping
                self.assertTrue((Path(tmp) / f"scene_{seg.index:02d}.wav").exists())
                prev_end = seg.start + seg.length
            self.assertTrue((Path(tmp) / "narration.md").exists())

    def test_without_tts_segments_are_saved_as_text(self):
        doc = Documentary.load(SCENARIO)
        with tempfile.TemporaryDirectory() as tmp:
            class Broken(SileroTTS):
                def load(self):
                    raise RuntimeError("no model")
            from prokv.voice import documentary as vd
            original = vd.SileroTTS
            vd.SileroTTS = Broken
            try:
                track = build_voice_track(doc, Path(tmp))
            finally:
                vd.SileroTTS = original
            self.assertFalse(track.available)
            self.assertEqual(len(list(Path(tmp).glob("scene_*.txt"))), 10)
            self.assertIn("estimated", (Path(tmp) / "narration.md").read_text(encoding="utf-8"))


@unittest.skipUnless(shutil.which("ffmpeg"), "FFmpeg not installed")
class SoundtrackTest(unittest.TestCase):
    def test_music_cue_is_mixed_in_its_slot_and_missing_files_stay_silent(self):
        from prokv.export.soundtrack import load_cues, mix_soundtrack

        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            subprocess.run(["ffmpeg", "-v", "error", "-f", "lavfi", "-i", "sine=f=440:d=6", str(tmp / "a.mp3")],
                           check=True)
            (tmp / "cues.json").write_text(json.dumps({"cues": [
                {"artist": "A", "track": "T", "start": 2.0, "end": 4.0, "file": "a.mp3", "gain_db": -6},
                {"artist": "B", "track": "U", "start": 5.0, "end": 7.0, "file": "missing.mp3"}]}))
            wav, used, missing = mix_soundtrack(8.0, tmp / "mix.wav", None, load_cues(tmp / "cues.json"))
            self.assertEqual((len(used), len(missing)), (1, 1))
            self.assertAlmostEqual(wav_duration(wav), 8.0, places=1)
            self.assertLess(_peak(wav, 0.2, 1.8), 50)        # silent before the cue
            self.assertGreater(_peak(wav, 2.5, 3.5), 1000)   # music inside the cue
            self.assertLess(_peak(wav, 5.2, 6.8), 50)        # missing file: silent slot


if __name__ == "__main__":
    unittest.main()
