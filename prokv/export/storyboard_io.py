"""storyboard.json: the editable plan between text analysis and rendering."""

from __future__ import annotations

import json
from pathlib import Path

from prokv.models import Storyboard


def save_storyboard(storyboard: Storyboard, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(storyboard.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def load_storyboard(path: Path) -> Storyboard:
    return Storyboard.from_dict(json.loads(path.read_text(encoding="utf-8")))
