# Prok-V — editorial infographic Reels from text

Prok-V turns plain text into a vertical motion-infographic video (9:16, 1080×1920 MP4).
You give it a text or a topic; it splits it into scenes, picks a layout for each one,
sets the typography and graphics, animates them and encodes the video.

Everything is generated programmatically with **Pillow** (graphics and frames) and
**FFmpeg** (encoding). No AI image generation, no photos, no paid APIs, no API keys.

## Workflow

```
text ─► 1. content    split into scenes, choose a template, condense wording, timing
     ─► 2. layout     scene template places elements on the grid
     ─► 3. graphics   lines, frames, blocks, rings, arrows, vinyl, paper texture
     ─► 4. typography serif/sans/mono roles, wrapping, auto-fit, highlighted words
     ─► 5. animation  fade, slide, mask reveal, line drawing, word-by-word, count-up
     ─► 6. render     frames: background, header, elements, scene transitions
     ─► 7. export     FFmpeg → H.264 MP4 1080×1920 (+ storyboard.json)
```

| Folder | What it does |
|--------|--------------|
| `prokv/content/` | `analyzer.py`: text → `Storyboard` (scenes). `text.py`: sentences, numbers, years, keywords, condensing |
| `prokv/layout/` | `grid.py`: safe area. `templates/`: the 9 scene templates + shared `SceneContext` |
| `prokv/graphics/` | `shapes.py`: graphic sprites. `texture.py`: paper background with grain |
| `prokv/typography/` | `fonts.py`: fonts by role. `text.py`: layout, fitting, per-word sprites |
| `prokv/animation/` | `easing.py`, `motion.py` (motion presets), `element.py` (animated element), `timeline.py` |
| `prokv/render/` | `renderer.py`: storyboard → frames, transitions, header and progress line |
| `prokv/export/` | `ffmpeg.py`: MP4 encoding. `storyboard_io.py`: save/load `storyboard.json` |
| `prokv/style.py` | **The visual system**: palette, fonts, sizes, spacing, motion, scene themes |
| `prokv/pipeline.py`, `prokv/cli.py` | Wiring and the command line |

## Scene templates

The analyzer picks a template from the content of each part of the text:

| # | Template | Chosen when the text has… | Looks like |
|---|----------|---------------------------|------------|
| 01 | `statement` | the opening title, or a plain thought | Large serif headline, key word in burgundy italic, thin drawn circle |
| 02 | `big_number` | a percentage, money, a large number | Number counts up; ring chart for % (alt: huge left-aligned number) |
| 03 | `comparison` | "раньше… / сегодня…", "не X, а Y", "X vs Y" | Two columns, divider line drawing down, "vs" badge |
| 04 | `list` | bullet points, or "Heading: a, b, c" | Numbered rows with hairlines drawing across |
| 05 | `timeline` | two or more years | Vertical line drawing down, dots, years, short captions |
| 06 | `quote` | text in «quotes» (+ "— говорит …") | Dark ground, oversized quote mark, italic lines rising |
| 07 | `diagram` | "сначала… затем… потом…", "→", "приводит к" | Steps in frames joined by arrows; the result step filled |
| 08 | `split` | "X — это Y" (definition) | Burgundy panel with the term, explanation below |
| 09 | `conclusion` | "Итог: …", "В итоге…", or the last paragraph | Vinyl record, centred takeaway |

The same template twice in a row switches to an alternative layout (`variant: "alt"`),
and two plain statements in a row become a statement + split, so screens don't repeat.

## How the text is analysed

The analyzer (`RuleBasedAnalyzer`) is rule-based and runs offline (Russian and English):

- **Scenes**: blank lines separate scenes; long paragraphs are split into sentences,
  and sentences with their own structure (numbers, years, quotes, steps, contrasts)
  get their own scene. At most `--max-scenes` (default 12) scenes are kept.
- **Wording**: text on screen is shortened, never rewritten: fillers ("на самом деле",
  "конечно"…) and parentheses are removed and sentences are cut at clause boundaries
  (headline ≤ 8–12 words, secondary line ≤ 14). Quotes are kept verbatim.
- **Highlights**: one key word per headline (proper nouns and long nouns preferred).
- **Duration**: from the number of words on screen and elements (3.4–7.5 s per scene).

You can steer it with light markup in the text:

```
# Title of the video          → opening scene and header title
(blank line) or ---           → scene boundary
- item / 1. item              → list scene
**word**                      → highlight this word
```

The result is saved as `storyboard.json`. Edit it by hand (wording, `kind`,
`duration_s`, `highlights`) and re-render with `--from-plan`.
The analyzer is a replaceable class (`ContentAnalyzer`), so a smarter one can be
plugged in later without touching layout or rendering.

## Visual system: WARM × STRICT

Warm, strict, intellectual, calm, adult, editorial, minimal; vinyl, music, culture,
restaurants and wine bars. Cream/beige is the light contrast, burgundy the main
accent, olive the calm secondary accent. Only these colours are used:

| Burgundy | Dark Burgundy | Warm Cream | Paper Beige | Dark Olive | Muted Olive | Espresso | Warm Black |
|---|---|---|---|---|---|---|---|
| `#5A171B` | `#351315` | `#E8DDC8` | `#CBB99A` | `#303126` | `#535342` | `#2B201A` | `#171512` |

Everything visual lives in `prokv/style.py` (`VisualStyle`):

- `palette` and `themes` (cream, paper, burgundy, espresso, olive) and
  `scene_themes` (which theme each template uses);
- `fonts`: roles `display`, `display_italic`, `serif`, `serif_italic`, `text`, `mono`,
  each a list of font files (first installed one wins; all support Cyrillic);
- `type`: font sizes and leading; `spacing`: margins, safe areas, line weights;
- `motion`: speed, entrance duration, word stagger, easing, drift, transition
  (`wipe_up`, `fade`, `cut`) and scene-timing rules;
- `grain`, `show_header`, `show_progress`.

Change it without touching code by passing a JSON file with only the settings you
want to override — see `examples/style_override.json`:

```bash
python -m prokv --file my_text.txt --style examples/style_override.json
```

## Quick start

Requirements: Python 3.10+, Pillow, and [FFmpeg](https://ffmpeg.org/download.html)
on your `PATH`:

- macOS: `brew install ffmpeg`
- Ubuntu/Debian: `sudo apt install ffmpeg fonts-liberation`
- Windows: `winget install ffmpeg`, then open a new terminal

```bash
pip install -e .                                   # installs Pillow and the `prokv` command

python -m prokv --file examples/demo_ru.txt         # → output/video.mp4 + output/storyboard.json
python -m prokv "Ваш текст или тема ролика…"         # text as an argument
cat text.txt | python -m prokv --file -             # from stdin
python -m prokv --file text.txt --plan-only         # only storyboard.json, to review/edit first
python -m prokv --from-plan output/storyboard.json  # render an (edited) storyboard

python -m unittest discover -s tests
```

Options: `--out DIR` (default `output/`), `--style FILE.json`, `--max-scenes N`,
`--fps N` (default 30). The command prints the scene plan before rendering.

Rendering takes roughly 0.8× the video length on a laptop CPU (a 60 s video ≈ 50 s).

## Adding a template

Create `prokv/layout/templates/t10_mine.py` with a function decorated by
`@template("mine")` that adds elements through the `SceneContext` helpers
(`fit`, `place_words`, `place_lines`, `label`, `kicker`, `rule`, `add`), import it in
`templates/__init__.py`, map it to a theme in `style.scene_themes`, and teach the
analyzer when to choose it.
