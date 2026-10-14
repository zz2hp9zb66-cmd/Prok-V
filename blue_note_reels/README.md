# Blue Note Reels — «Почему обложки Blue Note стали классикой?»

Vertical documentary Reels (1080×1920, 30 fps, H.264 + AAC) built by Prok-V from
`blue_note_scenario.json` and the images listed in `image_manifest.json`.

## Rebuild

```bash
# from the Prok-V folder, with the project's environment active
python -m prokv --story blue_note_reels/blue_note_scenario.json            # voice: Silero eugene
python -m prokv --story blue_note_reels/blue_note_scenario.json --no-voice # picture only
```

- With Silero available → `output/BLUE_NOTE_REELS_FINAL.mp4`.
- Without it → `output/BLUE_NOTE_REELS_PREVIEW_NO_VOICE.mp4` (estimated timings).

## Folders

| Path | Contents |
|------|----------|
| `assets/blue_note/` | original images, `<ID>_…` (not in git; never modified) |
| `assets/music/` | `music.json` + a licensed instrumental hard-bop file you provide |
| `audio/` | `S01.txt…S07.txt` narration, `S01.wav…` voice per scene, `voice.wav`, `soundtrack.wav` |
| `scenes/` | scene settings live in `blue_note_scenario.json` (one entry per scene) |
| `renders/` | `control_frames/` (2 per scene + contact sheet), `render_config.json`, video without subtitles |
| `output/` | final MP4, `.ru.srt` subtitles, `qc_report.md` |

## How it works

- **Timing.** Each scene lasts at least its planned length and longer when its speech needs it (voice starts 0.4 s
  into the scene). The whole text is kept: no speed-up, no cuts.
- **Images.** Images are shown through animated crops (Ken Burns, detail moves, mask reveals) of the originals;
  missing IDs get a neutral placeholder and are listed in the report.
- **Annotations.** Lines and tags mark crop, text areas and negative space using the named regions in
  `image_manifest.json` — they sit on top of the cover, the cover itself is untouched.
- **Subtitles.** A separate switchable track + `.srt` (not burned into the picture).
- **Music.** Put a licensed track at `assets/music/background_hard_bop.mp3` (or change `music.json`): it plays
  under the voice at −20 dB with fades. Nothing is downloaded.
