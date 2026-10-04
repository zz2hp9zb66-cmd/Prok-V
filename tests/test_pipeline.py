import json
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from PIL import Image

from prokv import Pipeline, VideoSpec
from prokv.captions import build_captions
from prokv.export import RenderPlanExporter, load_render_plan
from prokv.models import Keyframe
from prokv.generation import PlaceholderGenerator
from prokv.rendering import FrameRenderer, interpolate
from prokv.style import WARM_STRICT, hex_to_rgb


def _distance(a, b):
    return max(abs(x - y) for x, y in zip(a, b))


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


class StyleTest(unittest.TestCase):
    def test_placeholders_use_palette_colors(self):
        palette = [hex_to_rgb(c) for c in WARM_STRICT.palette.colors()]
        with tempfile.TemporaryDirectory() as tmp:
            for image in PlaceholderGenerator(width=96, height=128).generate("palette", 6, Path(tmp)):
                with Image.open(image.path) as im:
                    corner = im.convert("RGB").getpixel((2, 2))
                self.assertLess(min(_distance(corner, c) for c in palette), 50, corner)

    def test_placeholder_schemes_come_from_palette(self):
        palette = set(WARM_STRICT.palette.colors())
        for scheme in WARM_STRICT.placeholder.schemes:
            self.assertTrue(set(scheme) <= palette, scheme)

    def test_background_is_cream(self):
        with tempfile.TemporaryDirectory() as tmp:
            plan = json.loads(_plan(Path(tmp)).read_text())
            self.assertEqual(plan["composition"]["background"], WARM_STRICT.palette.cream)


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
            # At t=0 nothing has appeared yet: only the grainy cream background.
            cream = hex_to_rgb(WARM_STRICT.background)
            self.assertLess(_distance(first.resize((1, 1), Image.Resampling.BOX).getpixel((0, 0)), cream), 4)
            self.assertEqual(first.getpixel((540, 960)), renderer.background.getpixel((540, 960)))
            self.assertNotEqual(later.getpixel((540, 960)), renderer.background.getpixel((540, 960)))


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
