import json
import tempfile
import unittest
from pathlib import Path

from prokv import Pipeline, VideoSpec
from prokv.captions import build_captions


class PipelineTest(unittest.TestCase):
    def test_run_writes_images_and_render_plan(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            plan_path = Pipeline().run("city at dusk", ["Hello", "World"], out, image_count=3)

            images = sorted((out / "images").glob("*.png"))
            self.assertEqual(len(images), 3)
            self.assertTrue(images[0].read_bytes().startswith(b"\x89PNG"))

            plan = json.loads(plan_path.read_text())
            self.assertEqual((plan["spec"]["width"], plan["spec"]["height"]), (1080, 1920))
            self.assertEqual(len(plan["composition"]["layers"]), 3)
            self.assertEqual(len(plan["animation"]["tracks"]), 3)
            self.assertEqual([c["text"] for c in plan["captions"]], ["Hello", "World"])

    def test_layers_stay_on_canvas(self):
        spec = VideoSpec()
        with tempfile.TemporaryDirectory() as tmp:
            pipeline = Pipeline()
            images = pipeline.generator.generate("x", 5, Path(tmp))
            for layer in pipeline.compositor.compose(images, spec).layers:
                self.assertGreaterEqual(layer.x, 0)
                self.assertGreaterEqual(layer.y, 0)
                self.assertLessEqual(layer.x + layer.width, spec.width)
                self.assertLessEqual(layer.y + layer.height, spec.height)

    def test_captions_split_duration(self):
        caps = build_captions(["a", " ", "b"], VideoSpec(duration_s=8))
        self.assertEqual([(c.text, c.start_s, c.end_s) for c in caps], [("a", 0, 4), ("b", 4, 8)])


if __name__ == "__main__":
    unittest.main()
