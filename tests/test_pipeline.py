import json
import shutil
import subprocess
import tempfile
import unittest
from dataclasses import fields
from pathlib import Path

from prokv.config import VideoSpec
from prokv.content import text as tx
from prokv.content.analyzer import RuleBasedAnalyzer
from prokv.export import load_storyboard, save_storyboard
from prokv.layout.templates import TEMPLATES
from prokv.models import SCENE_KINDS, Scene, SceneContent, Storyboard
from prokv.pipeline import Pipeline
from prokv.render import StoryboardRenderer
from prokv.style import DEFAULT_STYLE, WARM_STRICT, load_style

DEMO = Path(__file__).resolve().parent.parent / "examples" / "demo_ru.txt"


def _kinds(text):
    return [s.kind for s in RuleBasedAnalyzer().analyze(text).scenes]


class TextTest(unittest.TestCase):
    def test_sentences_keep_abbreviations(self):
        self.assertEqual(tx.split_sentences("В 1948 г. вышла пластинка. Потом CD!"),
                         ["В 1948 г. вышла пластинка.", "Потом CD!"])

    def test_numbers_and_years(self):
        nums = tx.find_numbers("В 2023 году продажи выросли на 10% и превысили 1,4 миллиарда долларов")
        self.assertEqual([(n.display, n.is_year) for n in nums],
                         [("2023", True), ("10%", False), ("1,4 млрд $", False)])
        self.assertEqual(tx.key_number("продажи выросли на 10%").display, "+10%")

    def test_condense_respects_limit_and_clauses(self):
        self.assertEqual(tx.condense("На самом деле винил, конечно, очень важен для культуры", 10),
                         "Винил очень важен для культуры")
        short = tx.condense("Раньше музыку слушали фоном, в случайных плейлистах, без внимания к альбому", 6)
        self.assertLessEqual(tx.word_count(short), 6)

    def test_keywords_prefer_nouns(self):
        self.assertEqual(tx.keywords("Почему винил звучит иначе"), ["винил"])


class AnalyzerTest(unittest.TestCase):
    def test_demo_text_uses_many_templates(self):
        board = RuleBasedAnalyzer().analyze(DEMO.read_text(encoding="utf-8"))
        kinds = [s.kind for s in board.scenes]
        self.assertEqual(board.title, "Винил возвращается")
        self.assertEqual(kinds[0], "statement")
        self.assertEqual(kinds[-1], "conclusion")
        for kind in ("big_number", "timeline", "comparison", "list", "split", "diagram", "quote"):
            self.assertIn(kind, kinds)
        for a, b in zip(kinds, kinds[1:]):
            self.assertFalse(a == b == "statement")

    def test_scene_types_from_content(self):
        self.assertIn("big_number", _kinds("Выручка выросла на 35% за год."))
        self.assertIn("timeline", _kinds("В 1990 году открылся первый бар. В 2010 году их стало сто."))
        self.assertIn("list", _kinds("Что важно:\n- свет\n- звук\n- вино"))
        self.assertIn("quote", _kinds("«Музыка — это тишина между нотами», — говорил Дебюсси."))
        self.assertIn("diagram", _kinds("Сначала мы слушаем, затем выбираем, потом покупаем пластинку."))
        self.assertIn("split", _kinds("Сомелье — это человек, который подбирает вино к блюдам и настроению."))
        self.assertIn("comparison", _kinds("Раньше бары были шумными. Сегодня гости ищут тишину."))
        self.assertIn("conclusion", _kinds("Первая мысль здесь. Итог: слушайте внимательно."))

    def test_long_text_is_condensed(self):
        board = RuleBasedAnalyzer().analyze(DEMO.read_text(encoding="utf-8"))
        for scene in board.scenes:
            self.assertLessEqual(tx.word_count(scene.content.headline), 14)
            self.assertGreaterEqual(scene.duration_s, DEFAULT_STYLE.motion.scene_min_s)
            self.assertLessEqual(scene.duration_s, DEFAULT_STYLE.motion.scene_max_s)

    def test_max_scenes(self):
        board = RuleBasedAnalyzer(max_scenes=5).analyze(DEMO.read_text(encoding="utf-8"))
        self.assertEqual(len(board.scenes), 5)


class StyleTest(unittest.TestCase):
    def test_themes_use_only_palette_colors(self):
        palette = set(WARM_STRICT.palette.colors())
        for name, theme in WARM_STRICT.themes.items():
            for f in fields(theme):
                self.assertIn(getattr(theme, f.name), palette, f"{name}.{f.name}")

    def test_every_template_has_a_theme(self):
        self.assertEqual(set(TEMPLATES), set(SCENE_KINDS))
        self.assertTrue(set(SCENE_KINDS) <= set(WARM_STRICT.scene_themes))

    def test_json_override(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "style.json"
            path.write_text(json.dumps({"motion": {"speed": 1.5}, "type": {"display": 100},
                                        "themes": {"cream": {"accent": "#535342"}},
                                        "scene_themes": {"quote": "olive"}}))
            style = load_style(path)
        self.assertEqual(style.motion.speed, 1.5)
        self.assertEqual(style.type.display, 100)
        self.assertEqual(style.themes["cream"].accent, "#535342")
        self.assertEqual(style.themes["cream"].background, WARM_STRICT.themes["cream"].background)
        self.assertEqual(style.scene_themes["quote"], "olive")


class RenderTest(unittest.TestCase):
    def test_every_template_renders(self):
        content = SceneContent(kicker="Тест", headline="Заголовок сцены", body="Второстепенный текст",
                               number="+42%", items=["Первый", "Второй", "Третий"],
                               pairs=[["1990", "Начало"], ["2020", "Сейчас"]], quote="Короткая цитата здесь",
                               author="Автор", highlights=["сцены"])
        board = Storyboard("Тест", "ru", [Scene(kind, 2.0, content) for kind in SCENE_KINDS])
        renderer = StoryboardRenderer(board)
        for scene in renderer.scenes:
            start = renderer.render(scene.start + 0.01)
            settled = renderer.render(scene.start + 1.6)
            self.assertEqual(settled.size, (1080, 1920))
            self.assertNotEqual(start.tobytes(), settled.tobytes(), scene.context.elements[:1])

    def test_storyboard_round_trip(self):
        board = RuleBasedAnalyzer().analyze(DEMO.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as tmp:
            loaded = load_storyboard(save_storyboard(board, Path(tmp) / "storyboard.json"))
        self.assertEqual(loaded, board)


@unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "FFmpeg not installed")
class VideoExportTest(unittest.TestCase):
    def test_exports_vertical_mp4(self):
        with tempfile.TemporaryDirectory() as tmp:
            pipeline = Pipeline(spec=VideoSpec(fps=5))
            video = pipeline.run("Выручка выросла на 35% за год. Итог: это работает.", Path(tmp))
            probe = subprocess.run(
                ["ffprobe", "-v", "error", "-select_streams", "v:0", "-count_frames",
                 "-show_entries", "stream=codec_name,width,height,nb_read_frames", "-of", "json", str(video)],
                capture_output=True, text=True, check=True)
            stream = json.loads(probe.stdout)["streams"][0]
            board = load_storyboard(Path(tmp) / "storyboard.json")
            self.assertEqual(stream["codec_name"], "h264")
            self.assertEqual((stream["width"], stream["height"]), (1080, 1920))
            self.assertEqual(int(stream["nb_read_frames"]), round(board.duration_s * 5))


if __name__ == "__main__":
    unittest.main()


class TrackMapTest(unittest.TestCase):
    MAPS = Path(__file__).resolve().parent.parent / "examples" / "maps"

    def test_keyframes(self):
        from PIL import Image as _Image

        from prokv.animation.stage import Node
        node = Node(_Image.new("RGBA", (4, 4)), 100, 100)
        node.show(1.0, 0.5)
        node.animate(2.0, 1.0, x=200)
        self.assertEqual(node.value(0.5)["opacity"], 0.0)
        self.assertAlmostEqual(node.value(1.6)["opacity"], 1.0)
        self.assertAlmostEqual(node.value(3.5)["x"], 200)
        with self.assertRaises(ValueError):
            node.animate(1.0, 0.2, x=0)

    def test_episodes_build_and_render(self):
        from prokv.content.track_map import Episode
        from prokv.layout.maps import build_episode
        from prokv.render.stage_renderer import StageRenderer

        for path in sorted(self.MAPS.glob("*.json")):
            with self.subTest(episode=path.name):
                ep = Episode.load(path)
                stage, overlay = build_episode(ep)
                renderer = StageRenderer(stage, 30, 4, overlay)
                self.assertEqual(renderer.frame_count, round(ep.duration * 30))
                times = [sec.start + sec.length * 0.7 for sec in ep.sections]
                frames = [renderer.render(t) for t in times]
                self.assertTrue(all(f.size == (1080, 1920) for f in frames))
                self.assertEqual(len({f.tobytes() for f in frames}), len(frames))

    def test_all_section_types_are_used(self):
        from prokv.content.track_map import Episode
        from prokv.layout.maps import SECTIONS

        used = {sec.type for path in self.MAPS.glob("*.json") for sec in Episode.load(path).sections}
        self.assertEqual(used, set(SECTIONS))

    def test_episode_validation(self):
        from prokv.content.track_map import Episode

        base = json.loads((self.MAPS / "001_billie_jean.json").read_text(encoding="utf-8"))
        broken = {
            "unknown pair": lambda d: d["sections"][6].update(pair=["DRUMS", "TUBA"]),
            "gap in timing": lambda d: d["sections"][1].update(start="0:04"),
            "unknown type": lambda d: d["sections"][0].update(type="fireworks"),
        }
        for name, breaker in broken.items():
            data = json.loads(json.dumps(base))
            breaker(data)
            with self.subTest(name), tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / "bad.json"
                path.write_text(json.dumps(data), encoding="utf-8")
                with self.assertRaises(ValueError):
                    Episode.load(path)


if __name__ == "__main__":
    unittest.main()
