# Prok-V — Visual Content Generator

Prok-V turns a text prompt into a vertical social-media video (9:16, 1080×1920).

> **Status: base architecture only.** Every stage runs end-to-end with free, offline
> placeholders. No paid APIs, no API keys, and no third-party packages are required.

## The workflow

```
 text prompt ──► 1. Generate ──► 2. Compose ──► 3. Animate ──► 4. Captions ──► 5. Export
                   images         collage        keyframes      user text       9:16 video
```

| # | Stage | Module | What it will do | Current placeholder |
|---|-------|--------|-----------------|---------------------|
| 1 | Generate | `prokv/generation.py` | Create images from the prompt with an image model | Solid-colour PNGs derived from the prompt |
| 2 | Compose | `prokv/composition.py` | Arrange images into an editorial/collage layout | Staggered left/right cascade with a slight tilt |
| 3 | Animate | `prokv/animation.py` | Move, scale, fade and reveal collage elements | Each layer slides up and fades in, one after another |
| 4 | Captions | `prokv/captions.py` | Place and time the user's own text | Splits the duration evenly between captions |
| 5 | Export | `prokv/export.py` | Render frames and encode an MP4 at 1080×1920 | Writes a JSON render plan (no video yet) |

`prokv/pipeline.py` wires the stages together. The data passed between them is
defined in `prokv/models.py`: `GeneratedImage` → `Composition` (of `Layer`s) →
`Animation` (of `Keyframe`s) + `Caption`s → `Project`.

Each stage is an abstract base class (`ImageGenerator`, `Compositor`, `Animator`,
`Exporter`) with one default implementation, so a real tool can replace a
placeholder without changing the rest of the pipeline:

```python
from prokv import Pipeline

pipeline = Pipeline(generator=MyRealImageGenerator())  # other stages keep their defaults
pipeline.run("misty mountain sunrise", captions=["Day one", "Let's go"])
```

## Project layout

```
prokv/
  config.py        VideoSpec: 1080×1920, 30 fps, duration
  models.py        Data objects shared by all stages
  generation.py    Stage 1 — ImageGenerator, PlaceholderGenerator
  composition.py   Stage 2 — Compositor, StaggeredCollageCompositor
  animation.py     Stage 3 — Animator, StaggeredRevealAnimator
  captions.py      Stage 4 — build_captions
  export.py        Stage 5 — Exporter, RenderPlanExporter
  pipeline.py      Runs the stages in order
  cli.py           Command-line entry point
tests/             Standard-library unittest suite
```

## Quick start

Requires Python 3.10+.

```bash
python -m prokv "neon city at night" --caption "Welcome" --caption "to the future"
python -m unittest discover -s tests
```

Options: `--images N` (default 4), `--duration SECONDS` (default 10), `--out DIR`
(default `output/`). The output folder contains `images/` and `render_plan.json`.

Or install it as a `prokv` command with `pip install -e .`.

## Roadmap

Decisions still open (each needs approval before it's added, especially
anything paid or needing an API key):

1. **Image generation**: a local open-source model or a hosted API.
2. **Frame rendering**: drawing each frame from the render plan (e.g. Pillow).
3. **Video encoding**: producing the MP4 (e.g. FFmpeg).
4. **Typography**: fonts and caption styling.
5. **More layouts and animations**: extra `Compositor` / `Animator` implementations.
