"""Project folder layout and JSON persistence."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel

from .schemas import AssetMeta, Project, Scene, Timeline

M = TypeVar("M", bound=BaseModel)

SUBDIRS = [
    "scenes",
    "assets/originals",
    "assets/meta",
    "assets/cutouts",
    "assets/masks",
    "assets/styled",
    "assets/backgrounds",
    "assets/textures",
    "assets/inbox",
    "previews",
    "renders",
    "output",
    "logs",
]


def read_model(path: Path, model: type[M]) -> M:
    return model.model_validate_json(path.read_text(encoding="utf-8"))


def write_model(path: Path, obj: BaseModel) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = obj.model_dump(mode="json")
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


class ProjectDir:
    def __init__(self, root: Path):
        self.root = Path(root).resolve()

    # --- paths -------------------------------------------------------------
    @property
    def project_file(self) -> Path:
        return self.root / "project.json"

    @property
    def timeline_file(self) -> Path:
        return self.root / "timeline.json"

    @property
    def script_file(self) -> Path:
        return self.root / "script.md"

    def scene_file(self, scene_id: str) -> Path:
        return self.root / "scenes" / scene_id / "scene.json"

    def meta_file(self, asset_id: str) -> Path:
        return self.root / "assets" / "meta" / f"{asset_id}.json"

    def rel(self, path: Path) -> str:
        return Path(path).resolve().relative_to(self.root).as_posix()

    def abs(self, rel: str) -> Path:
        return self.root / rel

    # --- io ----------------------------------------------------------------
    def init(self, project: Project) -> None:
        for d in SUBDIRS:
            (self.root / d).mkdir(parents=True, exist_ok=True)
        write_model(self.project_file, project)

    def project(self) -> Project:
        return read_model(self.project_file, Project)

    def timeline(self) -> Timeline:
        return read_model(self.timeline_file, Timeline)

    def save_timeline(self, timeline: Timeline) -> None:
        write_model(self.timeline_file, timeline)

    def scene_ids(self) -> list[str]:
        return sorted(p.parent.name for p in (self.root / "scenes").glob("*/scene.json"))

    def scene(self, scene_id: str) -> Scene:
        return read_model(self.scene_file(scene_id), Scene)

    def scenes(self) -> list[Scene]:
        return [self.scene(s) for s in self.scene_ids()]

    def save_scene(self, scene: Scene) -> None:
        write_model(self.scene_file(scene.id), scene)

    def meta(self, asset_id: str) -> AssetMeta:
        return read_model(self.meta_file(asset_id), AssetMeta)

    def save_meta(self, meta: AssetMeta) -> None:
        write_model(self.meta_file(meta.id), meta)

    def all_meta(self) -> list[AssetMeta]:
        return [read_model(p, AssetMeta) for p in sorted((self.root / "assets/meta").glob("*.json"))]
