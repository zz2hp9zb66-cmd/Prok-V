"""Scene templates. Each module registers one template under its scene kind.

To add a template: create a module with a function decorated by
@template("my_kind") that adds elements to the SceneContext, import it below,
and map "my_kind" to a theme in style.VisualStyle.scene_themes.
"""

from prokv.layout.templates import (  # noqa: F401  (imports register the templates)
    t01_statement,
    t02_big_number,
    t03_comparison,
    t04_list,
    t05_timeline,
    t06_quote,
    t07_diagram,
    t08_split,
    t09_conclusion,
)
from prokv.layout.templates.base import TEMPLATES, SceneContext

__all__ = ["TEMPLATES", "SceneContext"]
