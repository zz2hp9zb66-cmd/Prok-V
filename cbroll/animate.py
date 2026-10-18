"""Assign motion to approved scenes: layer entrances, idle motion, camera, transitions.

Choices are seeded per scene, so re-running gives the same result; change the
scene seed to get another variant. Variety rules:
  * neighbouring scenes never share a camera move or a transition type;
  * inside a scene, consecutive layers never share an entrance;
  * heroes of neighbouring scenes enter differently.
"""

from __future__ import annotations

import random

from .schemas import Animation, Camera, Layer, Pace, Scene, Timeline

CAMERA_MOVES = ["push_in", "pan_right", "tilt_up", "pull_out", "pan_left", "dutch"]
TRANSITIONS = ["paper_tear", "slide", "zoom", "wipe", "fade"]

ENTERS = {
    "shape": ["wipe", "unfold"],
    "photo": ["fade", "slide_up", "drop"],
    "hero": ["drop", "slide_left", "slide_right", "pop", "stop_motion"],
    "prop": ["pop", "stop_motion", "slide_right", "slide_left", "drop"],
    "headline": ["stamp", "wipe"],
    "text": ["typewriter", "pop", "wipe"],
}
IDLES = {
    "shape": ["none"],
    "photo": ["drift"],
    "hero": ["drift", "sway", "jitter"],
    "prop": ["sway", "jitter", "breathe", "drift"],
    "headline": ["breathe", "none"],
    "text": ["none", "jitter"],
}
STAGGER: dict[str, int] = {"slow": 10, "medium": 7, "fast": 4}
ENTER_LEN: dict[str, int] = {"slow": 20, "medium": 15, "fast": 10}


def _role(layer: Layer) -> str:
    if layer.kind in ("shape", "photo"):
        return layer.kind
    if layer.kind == "text":
        return "headline" if layer.id == "headline" else "text"
    return "hero" if layer.id.startswith("hero") else "prop"


def _pick(rnd: random.Random, options: list[str], avoid: set[str]) -> str:
    fresh = [o for o in options if o not in avoid]
    return rnd.choice(fresh or options)


def animate_scene(scene: Scene, duration: int, pace: Pace, prev_hero_enters: set[str], prev_camera: str | None) -> Scene:
    rnd = random.Random(scene.seed)
    stagger, length = STAGGER[pace], ENTER_LEN[pace]
    budget = int(duration * 0.6)  # everything has landed by 60% of the scene
    delay, last_enter = 0, None
    order = sorted((l for l in scene.layers if l.kind != "texture"), key=lambda l: (l.z, l.id))
    hero_enters: set[str] = set()
    for layer in order:
        role = _role(layer)
        avoid = {last_enter} | (prev_hero_enters if role == "hero" else set())
        enter = _pick(rnd, ENTERS[role], avoid)
        layer.anim = Animation(
            enter=enter,
            delay=min(delay, budget),
            duration=length + (6 if enter == "typewriter" else 0),
            idle=rnd.choice(IDLES[role]),
        )
        if role == "hero":
            hero_enters.add(enter)
        last_enter = enter
        delay += stagger if role != "shape" else stagger // 2
    for layer in scene.layers:
        if layer.kind == "texture":
            layer.anim = Animation(enter="none", delay=0, duration=1, idle="none")
    scene.camera = Camera(move=_pick(rnd, CAMERA_MOVES, {prev_camera} if prev_camera else set()), strength=1.0)
    prev_hero_enters.clear()
    prev_hero_enters.update(hero_enters)
    return scene


def animate_all(scenes: list[Scene], timeline: Timeline) -> tuple[list[Scene], Timeline]:
    durations = {e.scene: e.duration_frames for e in timeline.entries}
    heroes: set[str] = set()
    camera = None
    for scene in scenes:
        animate_scene(scene, durations[scene.id], timeline.pace, heroes, camera)
        camera = scene.camera.move
    rnd = random.Random(len(scenes))
    last = None
    for entry in timeline.entries:
        t = _pick(rnd, TRANSITIONS, {last} if last else set())
        entry.transition_out.type = t
        last = t
    return scenes, timeline
