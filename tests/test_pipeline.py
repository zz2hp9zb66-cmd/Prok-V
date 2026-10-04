import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from prokv import Pipeline, VideoSpec
from prokv.captions import build_captions
from prokv.export import RenderPlanExporter, load_render_plan
from prokv.models import Keyframe
from prokv.rendering import FrameRenderer, interpolate


def _plan(out: Path, **kwargs) -> Path:
    pipeline = Pipeline(exporter=RenderPlanExporter(), **kwargs)
    return pipeline.run("city at dusk", ["Hello", "Привет, мир"], out, image_count=3)


class PipelineTest(unittest.TestCase):
    def test_run_writes_images_and_render_plan(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            plan_path = _plan(out)

            images = sorted((out / "images").glob("*.png"))
            self.assertEqual(len(images), 3)
            self.assertTrue(images[0].read_bytes().startswith(b"\x89PNG"))

            plan = json.loads(plan_path.read_text())
            self.assertEqual((plan["spec"]["width"], plan["spec"]["height"]), (1080, 1920))
            self.assertEqual(len(plan["composition"]["layers"]), 3)
            self.assertEqual(len(plan["animation"]["tracks"]), 3)
            self.assertEqual([c["text"] for c in plan["captions"]], ["Hello", "Привет, мир"])
            self.assertEqual(plan["composition"]["layers"][0]["image"]["path"], "images/image_00.png")

    def test_render_plan_round_trips(self):
        with tempfile.TemporaryDirectory() as tmp:
            project = load_render_plan(_plan(Path(tmp)))
            self.assertTrue(project.composition.layers[0].image.path.is_file())
            self.assertEqual(project.captions[1].text, "Привет, мир")

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


class RenderingTest(unittest.TestCase):
    def test_interpolate_eases_between_keyframes(self):
        track = [Keyframe(0, opacity=0, easing="linear"), Keyframe(2, opacity=1)]
        self.assertAlmostEqual(interpolate(track, 1).opacity, 0.5)
        self.assertEqual(interpolate(track, -1).opacity, 0)
        self.assertEqual(interpolate(track, 5).opacity, 1)
        held = [Keyframe(0, opacity=0, easing="hold"), Keyframe(2, opacity=1)]
        self.assertEqual(interpolate(held, 1.9).opacity, 0)

    def test_layers_fade_in_over_time(self):
        with tempfile.TemporaryDirectory() as tmp:
            renderer = FrameRenderer(load_render_plan(_plan(Path(tmp))))
            first, later = renderer.render(0.0), renderer.render(5.0)
            self.assertEqual(first.size, (1080, 1920))
            bg = first.getpixel((0, 0))
            self.assertEqual(first.getcolors(1_000_000)[0][1], bg)  # plain background at t=0
            self.assertEqual(len(first.getcolors(1_000_000)), 1)
            self.assertGreater(len(later.getcolors(1_000_000)), 10)


@unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "FFmpeg not installed")
class VideoExportTest(unittest.TestCase):
    def test_exports_vertical_mp4(self):
        with tempfile.TemporaryDirectory() as tmp:
            spec = VideoSpec(fps=10, duration_s=1.5)
            video = Pipeline(spec=spec).run("test", ["Caption"], Path(tmp), image_count=2)
            probe = subprocess.run(
                ["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_frames",
                 "-show_entries", "stream=codec_name,width,height,nb_read_frames", "-of", "json", str(video)],
                capture_output=True, text=True, check=True,
            )
            stream = json.loads(probe.stdout)["streams"][0]
            self.assertEqual(stream["codec_name"], "h264")
            self.assertEqual((stream["width"], stream["height"]), (1080, 1920))
            self.assertEqual(int(stream["nb_read_frames"]), 15)
            self.assertTrue((Path(tmp) / "render_plan.json").is_file())


if __name__ == "__main__":
    unittest.main()
