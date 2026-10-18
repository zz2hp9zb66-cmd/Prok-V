"""cbroll command line. Every command works on a project folder and can target single scenes."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated, Optional

import typer

from . import analyze as analyze_mod
from . import animate as animate_mod
from . import compose as compose_mod
from . import cutout as cutout_mod
from . import render as render_mod
from . import storyboard
from . import testassets
from .project import ProjectDir
from .schemas import Pace, Project, Scene

app = typer.Typer(no_args_is_help=True, add_completion=False)

ProjectArg = Annotated[Path, typer.Argument(help="Project folder, e.g. projects/blue-note-test")]
ScenesOpt = Annotated[Optional[list[str]], typer.Option("--scene", "-s", help="Scene id(s); default: all")]


def _pd(path: Path) -> ProjectDir:
    pd = ProjectDir(path)
    if not pd.project_file.exists():
        raise typer.BadParameter(f"{path} is not a cbroll project (no project.json)")
    return pd


def _selected(pd: ProjectDir, scenes: list[str] | None) -> list[Scene]:
    return [pd.scene(s) for s in (scenes or pd.scene_ids())]


@app.command()
def init(path: ProjectArg, title: str = "", pace: Pace = "medium", language: str = "ru", seed: int = 1) -> None:
    """Create the project folder structure."""
    pd = ProjectDir(path)
    pd.init(Project(name=pd.root.name, title=title or pd.root.name, pace=pace, language=language, seed=seed))
    if not pd.script_file.exists():
        pd.script_file.write_text("# Сценарий\n\n", encoding="utf-8")
    typer.echo(f"project created: {pd.root}")


@app.command()
def analyze(path: ProjectArg, pace: Optional[str] = None) -> None:
    """Split script.md into scenes and compute durations. Keeps plans of scenes whose text is unchanged."""
    pd = _pd(path)
    project = pd.project()
    if pace:
        project.pace = pace  # type: ignore[assignment]
        from .project import write_model

        write_model(pd.project_file, project)
    scenes = analyze_mod.build_scenes(pd.script_file.read_text(encoding="utf-8"), project.pace, project.language, project.seed)
    old_timeline = pd.timeline() if pd.timeline_file.exists() else None
    for scene in scenes:
        if pd.scene_file(scene.id).exists():
            old = pd.scene(scene.id)
            if old.text == scene.text:
                scene = old
        pd.save_scene(scene)
    for stale in set(pd.scene_ids()) - {s.id for s in scenes}:
        pd.scene_file(stale).rename(pd.scene_file(stale).with_suffix(".removed.json"))
    timeline = analyze_mod.build_timeline(scenes, project.pace, project.language, project.fps, old_timeline)
    pd.save_timeline(timeline)
    for scene, entry in zip(scenes, timeline.entries):
        typer.echo(f"{scene.id}  {entry.duration_frames / project.fps:4.1f}s  {scene.words:2d} words  {scene.text[:70]}")


@app.command("apply-plan")
def apply_plan(path: ProjectArg, plan_file: Path) -> None:
    """Write visual plans (template + subjects) from a JSON file into scene.json files."""
    pd = _pd(path)
    plans = json.loads(plan_file.read_text(encoding="utf-8"))
    for scene_id, entry in plans.items():
        scene = pd.scene(scene_id)
        scene.template = entry.get("template", scene.template)
        scene.plan = scene.plan.model_validate(entry["plan"])
        pd.save_scene(scene)
        typer.echo(f"{scene_id}: {scene.template}, {len(scene.plan.subjects)} subjects")


@app.command("test-assets")
def test_assets(path: ProjectArg) -> None:
    """Generate offline placeholder photos (when image sources are not reachable)."""
    pd = _pd(path)
    for meta in testassets.generate(pd):
        typer.echo(f"{meta.id:14s} {meta.original}")


@app.command()
def cutout(path: ProjectArg, asset: Annotated[Optional[list[str]], typer.Option("--asset", "-a")] = None) -> None:
    """Remove backgrounds and build styled (paper-cut / print) versions."""
    pd = _pd(path)
    for meta in pd.all_meta():
        if asset and meta.id not in asset:
            continue
        cutout_mod.process(pd, meta)
        typer.echo(f"{meta.id:14s} -> {meta.styled}")


@app.command()
def compose(path: ProjectArg, scene: ScenesOpt = None, reseed: bool = False) -> None:
    """Lay out scenes from their plans. --reseed picks another random variant."""
    pd = _pd(path)
    for s in _selected(pd, scene):
        if reseed:
            s.seed += 1000
        compose_mod.compose_scene(pd, s)
        s.status = "draft"
        pd.save_scene(s)
        typer.echo(f"{s.id}: {len(s.layers)} layers")


@app.command()
def preview(path: ProjectArg, scene: ScenesOpt = None) -> None:
    """Render storyboard stills and the overview sheet / HTML page."""
    pd = _pd(path)
    render_mod.stills(pd, scene)
    typer.echo(storyboard.overview(pd))
    typer.echo(storyboard.html_page(pd))


@app.command()
def approve(path: ProjectArg, scenes: Annotated[list[str], typer.Argument()], note: str = "") -> None:
    """Mark scenes approved (use 'all' for every scene)."""
    pd = _pd(path)
    ids = pd.scene_ids() if scenes == ["all"] else scenes
    for sid in ids:
        s = pd.scene(sid)
        s.status = "approved"
        if note:
            s.notes.append(note)
        pd.save_scene(s)
    typer.echo(f"approved: {', '.join(ids)}")


@app.command("request-changes")
def request_changes(path: ProjectArg, scene: str, note: str) -> None:
    """Record a requested change; the scene goes back to needs_changes."""
    pd = _pd(path)
    s = pd.scene(scene)
    s.status = "needs_changes"
    s.notes.append(note)
    pd.save_scene(s)


@app.command("set-duration")
def set_duration(path: ProjectArg, scene: str, seconds: float) -> None:
    """Fix a scene duration by hand (e.g. to match a voice-over). Composition is untouched."""
    pd = _pd(path)
    tl = pd.timeline()
    for e in tl.entries:
        if e.scene == scene:
            e.duration_frames = round(seconds * tl.fps)
            e.locked = True
    pd.save_timeline(tl)


@app.command()
def animate(path: ProjectArg, force: bool = typer.Option(False, help="Animate even if some scenes are not approved")) -> None:
    """Assign entrances, idle motion, camera and transitions. Requires approved storyboard."""
    pd = _pd(path)
    scenes = pd.scenes()
    pending = [s.id for s in scenes if s.status != "approved"]
    if pending and not force:
        typer.echo(f"not approved yet: {', '.join(pending)} — run `cbroll approve` first", err=True)
        raise typer.Exit(1)
    scenes, tl = animate_mod.animate_all(scenes, pd.timeline())
    for s in scenes:
        pd.save_scene(s)
        heroes = [f"{l.id}:{l.anim.enter}" for l in s.layers if l.kind in ("cutout", "photo")]
        typer.echo(f"{s.id}: camera {s.camera.move}; {', '.join(heroes)}")
    pd.save_timeline(tl)
    typer.echo("transitions: " + " → ".join(e.transition_out.type for e in tl.entries[:-1]))


@app.command()
def render(path: ProjectArg, scene: Annotated[Optional[str], typer.Option("--scene", "-s")] = None) -> None:
    """Render the final MP4 (or one scene to renders/scenes/) and check it against the spec."""
    pd = _pd(path)
    project = pd.project()
    out = render_mod.scene_video(pd, scene) if scene else render_mod.video(pd, pd.abs("output/final.mp4"))
    info = render_mod.probe(out)
    problems = render_mod.check_spec(info, project.width, project.height, project.fps)
    typer.echo(f"{out}  {float(info['format']['duration']):.2f}s  " + ("OK" if not problems else "; ".join(problems)))
    if problems:
        raise typer.Exit(1)


@app.command()
def status(path: ProjectArg) -> None:
    """Scene list with status, duration and layer count."""
    pd = _pd(path)
    tl = {e.scene: e for e in pd.timeline().entries}
    for s in pd.scenes():
        e = tl[s.id]
        lock = " (locked)" if e.locked else ""
        typer.echo(f"{s.id}  {s.status:13s} {e.duration_frames / pd.timeline().fps:4.1f}s{lock}  {len(s.layers):2d} layers  {s.text[:60]}")


if __name__ == "__main__":
    app()
