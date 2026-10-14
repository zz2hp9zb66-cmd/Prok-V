"""Image-story scene context: grotesque typography, the scenario palette, image windows,
line annotations on covers and a registry of every text block for automatic QC.

Instagram Reels safe area used here: x 60–1020, y 250–1490 (top bar, caption and
buttons stay clear); text that leaves it is reported by `check_text_bounds`.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Callable

from PIL import Image, ImageDraw

from prokv.animation.stage import DynamicNode, Link, Node, Stage
from prokv.content.image_story import ImageStory, StoryScene
from prokv.graphics.imageview import FULL, ImageView, Move, fit_box
from prokv.style import DEFAULT_STYLE, Fonts
from prokv.typography import FontBook, label_sprite, text_sprite

SAFE = (60, 250, 1020, 1490)
LAYOUTS: dict[str, Callable[["StoryContext"], None]] = {}

GROTESK = replace(
    DEFAULT_STYLE.fonts,
    display=("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
             "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
             "/System/Library/Fonts/Supplemental/Arial Bold.ttf", "/Library/Fonts/Arial Bold.ttf",
             "C:/Windows/Fonts/arialbd.ttf"),
    text=("/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
          "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
          "/System/Library/Fonts/Supplemental/Arial.ttf", "/Library/Fonts/Arial.ttf", "C:/Windows/Fonts/arial.ttf"),
)


def layout(name: str):
    def register(fn):
        LAYOUTS[name] = fn
        return fn
    return register


@dataclass
class TextRecord:
    scene: str
    text: str
    x: float
    y: float
    w: int
    h: int
    fixed: str = ""          # set when the block was moved back inside the safe area


class StoryKit:
    def __init__(self, palette: dict) -> None:
        self.fonts = FontBook(GROTESK if isinstance(GROTESK, Fonts) else DEFAULT_STYLE.fonts)
        p = palette
        self.cream, self.ink = p.get("cream", "#F3EBDD"), p.get("ink", "#171717")
        self.blue, self.muted = p.get("blue", "#163C63"), p.get("muted_blue", "#7EA4BA")
        self.olive, self.burgundy = p.get("olive", "#77785C"), p.get("burgundy", "#653C43")

    def text(self, text: str, size: int, color: str, bold: bool = True) -> Image.Image:
        return text_sprite(text, self.fonts.get("display" if bold else "text", size), color)

    def label(self, text: str, size: int, color: str, tracking: int = 4, bold: bool = False) -> Image.Image:
        return label_sprite(text, self.fonts.get("display" if bold else "text", size), color, tracking)

    def fit(self, lines: list[str], size: int, max_w: float, bold: bool = True) -> int:
        role = "display" if bold else "text"
        while size > 16 and max(self.fonts.get(role, size).getlength(l) for l in lines) > max_w:
            size -= 2
        return size

    def wrap(self, text: str, size: int, max_w: float, color: str, bold: bool = False, align: str = "left",
             leading: float = 1.25) -> Image.Image:
        font = self.fonts.get("display" if bold else "text", size)
        lines, cur = [], ""
        for word in text.split():
            cand = f"{cur} {word}".strip()
            if cur and font.getlength(cand) > max_w:
                lines.append(cur)
                cur = word
            else:
                cur = cand
        lines.append(cur)
        sprites = [text_sprite(l, font, color) for l in lines]
        w = max(s.width for s in sprites)
        step = int(size * leading)
        out = Image.new("RGBA", (w, step * (len(lines) - 1) + sprites[-1].height), (0, 0, 0, 0))
        for i, s in enumerate(sprites):
            x = {"left": 0, "right": w - s.width}.get(align, (w - s.width) // 2)
            out.alpha_composite(s, (x, i * step))
        return out

    def stack(self, sprites: list[Image.Image], align: str = "left", gap: int = 8) -> Image.Image:
        w = max(s.width for s in sprites)
        out = Image.new("RGBA", (w, sum(s.height for s in sprites) + gap * (len(sprites) - 1)), (0, 0, 0, 0))
        y = 0
        for s in sprites:
            out.alpha_composite(s, ({"left": 0, "right": w - s.width}.get(align, (w - s.width) // 2), y))
            y += s.height + gap
        return out

    def block(self, w: int, h: int, color: str) -> Image.Image:
        return Image.new("RGBA", (max(w, 1), max(h, 1)), color)

    def dot(self, d: int, color: str) -> Image.Image:
        img = Image.new("RGBA", (d * 3, d * 3), (0, 0, 0, 0))
        ImageDraw.Draw(img).ellipse((0, 0, d * 3 - 1, d * 3 - 1), fill=color)
        return img.resize((d, d), Image.Resampling.LANCZOS)


@dataclass
class Window:
    node: DynamicNode
    view: ImageView
    x: float      # centre
    y: float
    w: int
    h: int

    def rect_at(self, box, t: float) -> tuple[float, float, float, float]:
        """Screen rectangle of a normalised source box, given the crop at time t."""
        cx0, cy0, cx1, cy1 = self.view.box_at(t)
        sw, sh = self.view.src.size
        sx = self.w / (cx1 - cx0)
        sy = self.h / (cy1 - cy0)
        left, top = self.x - self.w / 2, self.y - self.h / 2
        return (left + (box[0] * sw - cx0) * sx, top + (box[1] * sh - cy0) * sy,
                left + (box[2] * sw - cx0) * sx, top + (box[3] * sh - cy0) * sy)


class StoryContext:
    def __init__(self, stage: Stage, kit: StoryKit, story: ImageStory, scene: StoryScene,
                 start: float, end: float, index: int, texts: list[TextRecord]) -> None:
        self.stage, self.kit, self.story, self.scene = stage, kit, story, scene
        self.s, self.e, self.L = start, end, end - start
        self.index = index
        self.items: list[Node | Link] = []
        self.texts = texts
        self.last = index == len(story.scenes) - 1

    def at(self, fraction: float) -> float:
        """A moment inside the scene, as a fraction of its (speech-fitted) length."""
        return self.s + fraction * self.L

    # -- nodes -----------------------------------------------------------------

    def node(self, sprite: Image.Image, x: float, y: float, z: int = 4) -> Node:
        n = self.stage.node(sprite, x, y, z=z)
        self.items.append(n)
        return n

    def text(self, sprite: Image.Image, x: float, y: float, text: str, z: int = 6) -> Node:
        """A text node, registered for the bounds check and moved inside the safe area if needed."""
        x0, y0, x1, y1 = SAFE
        w, h = sprite.width, sprite.height
        nx = min(max(x, x0 + w / 2), x1 - w / 2) if w <= x1 - x0 else x
        ny = min(max(y, y0 + h / 2), y1 - h / 2) if h <= y1 - y0 else y
        fixed = f"moved by ({nx - x:+.0f}, {ny - y:+.0f}) px" if (abs(nx - x) > 0.5 or abs(ny - y) > 0.5) else ""
        self.texts.append(TextRecord(self.scene.id, text, nx, ny, w, h, fixed))
        return self.node(sprite, nx, ny, z)

    def window(self, image_id: str, x: float, y: float, w: int, h: int, moves: list[tuple[float, tuple]] | None,
               reveal: tuple[float, float, str] | None = None, z: int = 2) -> Window:
        src = self.story.open_image(image_id)
        view = ImageView(src, w, h, [Move(t, b) for t, b in (moves or [(self.s, FULL)])], reveal)
        n = self.stage.dynamic(view, x, y, z=z)
        self.items.append(n)
        return Window(n, view, x, y, w, h)

    def anchor(self, x: float, y: float) -> Node:
        return self.stage.node(self.kit.dot(2, self.kit.ink), x, y)

    def line(self, a: tuple[float, float], b: tuple[float, float], t: float, color: str, dur: float = 0.45,
             width: int = 2, **kwargs) -> Link:
        kwargs.setdefault("above", True)
        link = self.stage.link(self.anchor(*a), self.anchor(*b), color, t, dur=dur, width=width, **kwargs)
        self.items.append(link)
        return link

    def outline(self, rect, t: float, color: str, width: int = 3, step: float = 0.12) -> None:
        """Line animation: the four sides of a rectangle draw one after another."""
        x0, y0, x1, y1 = rect
        corners = [(x0, y0), (x1, y0), (x1, y1), (x0, y1), (x0, y0)]
        for i, (a, b) in enumerate(zip(corners, corners[1:])):
            self.line(a, b, t + i * step, color, dur=0.35, width=width, easing="ease_out")

    def tag(self, text: str, x: float, y: float, t: float, color: str, bg: str | None = None, size: int = 24) -> Node:
        """Small uppercase label, optionally on a solid chip so it stays readable over photos."""
        lab = self.kit.label(text, size, color, 4, bold=True)
        if bg:
            chip = self.kit.block(lab.width + 24, lab.height + 14, bg)
            chip.alpha_composite(lab, (12, 7))
            lab = chip
        n = self.text(lab, x + lab.width / 2, y + lab.height / 2, text, z=7)
        n.show(t, 0.4, dy=8)
        return n

    def mark(self) -> int:
        return len(self.items)

    def hide_since(self, mark: int, t: float, dur: float = 0.35) -> None:
        """Fade out everything added after `mark` (e.g. the annotations of a cover that is leaving)."""
        for item in self.items[mark:]:
            if isinstance(item, Link):
                item.t_hide, item.hide_dur = t, dur
            elif item.value(1e9)["opacity"] > 0:
                item.hide(max(t, item.keys[-1].t), dur, dy=0)

    def finish(self) -> None:
        t = self.e - (0.9 if self.last else 0.4)
        for item in self.items:
            if isinstance(item, Link):
                item.t_hide = t if item.t_hide is None else min(item.t_hide, t)
            elif item.value(1e9)["opacity"] > 0:
                item.hide(max(t, item.keys[-1].t), 0.4, dy=0)


def auto_fixes(texts: list[TextRecord]) -> list[str]:
    return [f"scene {r.scene}: “{r.text[:40]}” {r.fixed}" for r in texts if r.fixed]


def check_text_bounds(texts: list[TextRecord]) -> list[str]:
    problems = []
    x0, y0, x1, y1 = SAFE
    for r in texts:
        left, top = r.x - r.w / 2, r.y - r.h / 2
        if left < x0 - 1 or left + r.w > x1 + 1 or top < y0 - 1 or top + r.h > y1 + 1:
            problems.append(f"scene {r.scene}: “{r.text[:40]}” box ({left:.0f},{top:.0f})–"
                            f"({left + r.w:.0f},{top + r.h:.0f}) leaves the safe area {SAFE}")
    return problems


__all__ = ["LAYOUTS", "SAFE", "StoryContext", "StoryKit", "TextRecord", "Window", "auto_fixes", "check_text_bounds",
           "fit_box", "layout"]
