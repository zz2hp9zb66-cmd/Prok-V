"""Photo-led documentary Reels ("image stories"): a scenario of scenes built around
user-supplied images that are referenced by ID.

Files:
    <project>/<scenario>.json      scenes: narration, image IDs, on-screen texts, facts,
                                   animation notes, music parameters
    <project>/image_manifest.json  ID → expected file name, description, scenes, purpose
    <project>/assets/<images_dir>/ the original images, named "<ID>_..." (png/jpg/jpeg/webp)

Images are never modified: they are read, cropped/scaled in memory for the
composition, and a neutral placeholder is drawn when an ID has no file.
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

from PIL import Image, ImageDraw

from prokv.content.track_map import parse_time

IMAGE_EXT = (".png", ".jpg", ".jpeg", ".webp")


@dataclass
class ManifestImage:
    id: str
    file: str               # expected file name (without extension is fine)
    description: str
    scenes: list[str]
    purpose: str
    caption: str = ""       # on-screen caption; only facts that are confirmed
    regions: dict = field(default_factory=dict)   # named normalised boxes: key parts of the image
    year: str = ""
    artist: str = ""
    album: str = ""
    path: Path | None = None
    found: bool = False
    size: tuple[int, int] | None = None


@dataclass
class StoryScene:
    id: str
    title: str
    start: float            # planned (editing guide); final timing follows the speech
    end: float
    narration: str
    layout: str
    images: list[str]
    tts: str | None = None
    texts: dict = field(default_factory=dict)       # on-screen headings, labels, cards
    facts: list[str] = field(default_factory=list)
    animation: list[str] = field(default_factory=list)
    music: dict = field(default_factory=dict)

    @property
    def planned_length(self) -> float:
        return self.end - self.start

    @property
    def spoken(self) -> str:
        return self.tts or self.narration


@dataclass
class ImageStory:
    id: str
    title: str
    output: str
    scenes: list[StoryScene]
    images: dict[str, ManifestImage]
    root: Path
    palette: dict = field(default_factory=dict)
    speaker: str = "eugene"
    voice_lead_s: float = 0.4
    voice_tail_s: float = 0.35
    sentence_pause_s: float = 0.25
    music: dict = field(default_factory=dict)
    sources: list[str] = field(default_factory=list)
    notes: dict = field(default_factory=dict)

    @classmethod
    def load(cls, scenario: str | Path) -> "ImageStory":
        scenario = Path(scenario).resolve()
        root = scenario.parent
        data = json.loads(scenario.read_text(encoding="utf-8"))
        manifest = json.loads((root / data.pop("manifest", "image_manifest.json")).read_text(encoding="utf-8"))
        images_dir = root / manifest.get("images_dir", "assets/images")
        images = {}
        for item in manifest["images"]:
            img = ManifestImage(**item)
            img.path = find_image(images_dir, img.id)
            img.found = img.path is not None
            if img.found:
                with Image.open(img.path) as im:
                    img.size = im.size
            images[img.id] = img
        scenes = []
        for s in data.pop("scenes"):
            s = dict(s)
            s["start"], s["end"] = parse_time(s["start"]), parse_time(s["end"])
            scenes.append(StoryScene(**s))
        story = cls(scenes=scenes, images=images, root=root, **data)
        story.validate()
        return story

    def validate(self) -> None:
        from prokv.layout.image_story import LAYOUTS

        for sc in self.scenes:
            if sc.layout not in LAYOUTS:
                raise ValueError(f"scene {sc.id}: unknown layout {sc.layout!r}; available: {', '.join(LAYOUTS)}")
            for image_id in sc.images:
                if image_id not in self.images:
                    raise ValueError(f"scene {sc.id}: image ID {image_id} is not in the manifest")
            if re.search(r"[0-9A-Za-z]", sc.spoken):
                raise ValueError(f"scene {sc.id}: spoken text has digits/Latin letters — add a 'tts' form")

    @property
    def missing(self) -> list[ManifestImage]:
        return [img for img in self.images.values() if not img.found]

    def open_image(self, image_id: str) -> Image.Image:
        """The original image (RGB), or a neutral placeholder naming the missing ID."""
        img = self.images[image_id]
        if img.found:
            with Image.open(img.path) as im:
                return im.convert("RGB")
        return placeholder(img, self.palette)


def find_image(folder: Path, image_id: str) -> Path | None:
    """First file in `folder` whose name starts with the numeric ID (e.g. "06_…", "6-…")."""
    if not folder.is_dir():
        return None
    number = int(image_id)
    for path in sorted(folder.iterdir()):
        if path.suffix.lower() not in IMAGE_EXT:
            continue
        m = re.match(r"^(?:id[_-]?)?0*(\d+)(?:[_\-. ]|$)", path.name, re.IGNORECASE)
        if m and int(m.group(1)) == number:
            return path
    return None


def placeholder(img: ManifestImage, palette: dict) -> Image.Image:
    """Neutral stand-in: a flat panel with a thin frame and the missing ID — clearly not a photo."""
    w, h = (1200, 1200)
    bg = palette.get("muted_blue", "#7EA4BA")
    ink = palette.get("ink", "#171717")
    im = Image.new("RGB", (w, h), bg)
    d = ImageDraw.Draw(im)
    d.rectangle((40, 40, w - 41, h - 41), outline=ink, width=3)
    d.line((40, 40, w - 41, h - 41), fill=ink, width=1)
    d.line((40, h - 41, w - 41, 40), fill=ink, width=1)
    from prokv.typography import FontBook
    from prokv.style import DEFAULT_STYLE
    fonts = FontBook(DEFAULT_STYLE.fonts)
    d.rectangle((w / 2 - 330, h / 2 - 120, w / 2 + 330, h / 2 + 120), fill=bg)
    d.text((w / 2, h / 2 - 40), f"IMAGE ID {img.id}", font=fonts.get("text", 64), fill=ink, anchor="mm")
    d.text((w / 2, h / 2 + 50), "MISSING — PLACEHOLDER", font=fonts.get("mono", 34), fill=ink, anchor="mm")
    return im
