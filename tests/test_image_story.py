import json
import shutil
import tempfile
import unittest
from pathlib import Path

from prokv.content.image_story import ImageStory, find_image
from prokv.graphics.imageview import ImageView, Move, fit_box
from prokv.layout.image_story import auto_fixes, build_story, check_text_bounds
from prokv.render.stage_renderer import StageRenderer
from prokv.story import _estimate, _subtitle_cues

SCENARIO = Path(__file__).resolve().parent.parent / "blue_note_reels" / "blue_note_scenario.json"


def _timing(story):
    timing, t = [], 0.0
    for sc in story.scenes:
        length = max(sc.planned_length, story.voice_lead_s + _estimate(sc.spoken, 0.25) + story.voice_tail_s)
        timing.append((t, t + length))
        t += length
    return timing


class ImageStoryTest(unittest.TestCase):
    def test_find_image_by_numeric_id(self):
        with tempfile.TemporaryDirectory() as tmp:
            for name in ("06-coltrane.webp", "6_other.txt", "16_x.png", "notes.jpg"):
                (Path(tmp) / name).write_bytes(b"x")
            self.assertEqual(find_image(Path(tmp), "06").name, "06-coltrane.webp")
            self.assertIsNone(find_image(Path(tmp), "07"))

    def test_crop_never_leaves_the_image(self):
        for box in ((0.9, 0.9, 1.0, 1.0), (0.0, 0.0, 0.1, 0.5), (0.3, 0.2, 0.6, 0.4)):
            x0, y0, x1, y1 = fit_box(box, (1024, 672), 0.75)
            self.assertGreaterEqual(min(x0, y0), -1e-6)
            self.assertLessEqual(x1, 1024 + 1e-6)
            self.assertLessEqual(y1, 672 + 1e-6)
            self.assertAlmostEqual((x1 - x0) / (y1 - y0), 0.75, places=3)

    def test_imageview_leaves_the_source_untouched(self):
        from PIL import Image
        src = Image.new("RGB", (400, 300), "#163C63")
        before = src.tobytes()
        view = ImageView(src, 200, 200, [Move(0, (0, 0, 1, 1)), Move(1, (0.2, 0.2, 0.6, 0.6))], (0, 1, "up"))
        for t in (0, 0.5, 1.2):
            self.assertEqual(view(t).size, (200, 200))
        self.assertEqual(src.tobytes(), before)

    def test_scenario_builds_with_text_inside_safe_area(self):
        story = ImageStory.load(SCENARIO)
        self.assertEqual([s.id for s in story.scenes], [f"S0{i}" for i in range(1, 8)])
        stage, overlay, texts = build_story(story, _timing(story))
        self.assertEqual(check_text_bounds(texts), [])
        renderer = StageRenderer(stage, 30, 3, overlay)
        frames = [renderer.render(s + (e - s) * 0.6) for s, e in _timing(story)]
        self.assertEqual(len({f.tobytes() for f in frames}), 7)
        self.assertIsInstance(auto_fixes(texts), list)

    def test_unconfirmed_facts_stay_general(self):
        manifest = json.loads((SCENARIO.parent / "image_manifest.json").read_text(encoding="utf-8"))
        by_id = {m["id"]: m for m in manifest["images"]}
        self.assertNotIn("WOLFF (", by_id["05"]["caption"])      # no left/right attribution
        self.assertNotIn("WOLFF", by_id["06"]["caption"])         # photographer not credited
        scenario = json.loads(SCENARIO.read_text(encoding="utf-8"))
        s03 = next(s for s in scenario["scenes"] if s["id"] == "S03")
        self.assertIn("около", s03["facts"][0])

    def test_subtitles_cover_the_spoken_segment(self):
        cues = _subtitle_cues("Первое. Второе предложение длиннее.", 2.0, 4.0)
        self.assertEqual(len(cues), 2)
        self.assertAlmostEqual(cues[0][0], 2.0)
        self.assertAlmostEqual(cues[-1][1], 6.0)


if __name__ == "__main__":
    unittest.main()
