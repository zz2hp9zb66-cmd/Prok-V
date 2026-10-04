# Prok-V — Visual Content Generator

Prok-V turns a text prompt into a vertical social-media video (9:16, 1080×1920).

> **Status:** produces a real 1080×1920 MP4 with animated collage and captions.
> Images are still offline placeholders. No paid APIs or API keys are required.

## The workflow

```
 text prompt ──► 1. Generate ──► 2. Compose ──► 3. Animate ──► 4. Captions ──► 5. Export
                   images         collage        keyframes      user text       9:16 video
```

| # | Stage | Module | What it will do | Current placeholder |
|---|-------|--------|-----------------|---------------------|
| 1 | Generate | `prokv/generation.py` | Create images from the prompt with an image model | Solid-colour PNGs derived from the prompt |
| 2 | Compose | `prokv/composition.py` | Arrange images into an editorial/collage layout | Staggered left/right cascade with a slight tilt |
| 3 | Animate | `prokv/animation.py` | Move, scale, fade and reveal collage elements | Each layer slides in from its side, fades in and grows, then drifts slowly |
| 4 | Captions | `prokv/captions.py` | Place and time the user's own text | Splits the duration evenly between captions |
| 5 | Export | `prokv/export.py` + `prokv/rendering.py` | Render frames and encode an MP4 at 1080×1920 | ✅ Pillow draws frames, FFmpeg encodes H.264 MP4 |

`prokv/pipeline.py` wires the stages together. The data passed between them is
defined in `prokv/models.py`: `GeneratedImage` → `Composition` (of `Layer`s) →
`Animation` (of `Keyframe`s) + `Caption`s → `Project`.

### How a video is rendered

`VideoExporter` first writes `render_plan.json` (the whole `Project` as JSON), then
`FrameRenderer` (`prokv/rendering.py`) draws every frame with Pillow:

1. Each layer's image is cropped to its size, given a white border and a soft
   shadow, and rotated to its resting angle (done once per layer).
2. For each frame, the layer's keyframes are interpolated with their easing curve
   (`linear`, `ease_in`, `ease_out`, `ease_in_out`, `hold`) to get its offset,
   scale, rotation and opacity, and it is pasted onto the background.
3. Active captions are drawn on top in a rounded box, word-wrapped, with a short
   fade in/out, at the `top`, `center` or `bottom` position.

Raw frames are piped straight into FFmpeg (`libx264`, `yuv420p`, `+faststart`), so
no frame files are written to disk.

The look is configured separately from the motion: `LayerStyle` (border, shadow)
and `CaptionStyle` (font, size, colours, box, margins, fade) are passed to
`VideoExporter`; the motion comes from the `Animator`.

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
  export.py        Stage 5 — Exporter, RenderPlanExporter, VideoExporter
  rendering.py     Pillow frame renderer, LayerStyle, CaptionStyle
  pipeline.py      Runs the stages in order
  cli.py           Command-line entry point
tests/             Standard-library unittest suite
```

## Quick start

Requires Python 3.10+ and [FFmpeg](https://ffmpeg.org/download.html) on your `PATH`.

```bash
pip install -e .        # installs Pillow and the `prokv` command

# One prompt + captions -> output/video.mp4 (and output/render_plan.json)
python -m prokv "neon city at night" --caption "Welcome" --caption "to the future"

# Re-render an existing plan (e.g. after editing render_plan.json by hand)
python -m prokv --from-plan output/render_plan.json

python -m unittest discover -s tests
```

Options: `--images N` (default 4), `--duration SECONDS` (default 10), `--fps N`
(default 30), `--out DIR` (default `output/`), `--font PATH` (caption font; by
default a system bold sans-serif with Cyrillic support such as DejaVu Sans Bold),
`--plan-only` (write the JSON plan without rendering).

Captions share the video duration evenly, in the order given.

## Roadmap

Decisions still open (each needs approval before it's added, especially
anything paid or needing an API key):

1. **Image generation**: a local open-source model or a hosted API.
2. **Typography**: bundled brand fonts and richer caption styles.
3. **More layouts and animations**: extra `Compositor` / `Animator` implementations.
4. **Audio**: background music or voice-over.
