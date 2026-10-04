"""Stage 5: export the project as a 9:16 video."""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from dataclasses import asdict
from pathlib import Path

from prokv.models import Project


class Exporter(ABC):
    """Writes the final output for a project and returns its path."""

    @abstractmethod
    def export(self, project: Project, out_dir: Path) -> Path:
        ...


class RenderPlanExporter(Exporter):
    """Writes a JSON render plan describing the full video.

    Placeholder until a video renderer is chosen: the plan contains everything a
    renderer needs (canvas, layers, keyframes, captions) to draw each frame.
    """

    def export(self, project: Project, out_dir: Path) -> Path:
        out_dir.mkdir(parents=True, exist_ok=True)
        path = out_dir / "render_plan.json"
        path.write_text(json.dumps(asdict(project), indent=2, default=str))
        return path
