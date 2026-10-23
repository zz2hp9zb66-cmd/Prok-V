# Item icons (habits, goals, wishes)

## Where the images are
- `webp/<category>/<id>.webp` — **TOBI Icon Library v1**: 70 icons, 1024×1024, transparent background,
  no text, one visual style. Categories: `sport`, `health`, `learning`, `work`, `finance`, `life`.
- `manifest.json` — the library manifest (ids, Russian labels, categories, background colors).
- `LICENSE_ICONS.txt` — the icons are derived from Font Awesome Free (CC BY 4.0): the app must show attribution.

Everything is local and bundled with the app — no network.
Only WebP is bundled (half the size of the PNG set; pixel-identical layout, transparency kept).

## How the registry works
`features/icons/iconRegistry.ts`:
- `ICON_LIBRARY` — every icon offered in the picker, in picker order:
  `{ id, label, glyph: { kind: 'image', source: require('@/assets/icons/webp/…') }, color }`.
- `DEFAULT_ICONS` — universal icon per type (`default_habit`, `default_goal`, `default_wish`), used when
  nothing was chosen or the stored id is unknown.
- SQLite stores only the id: `habits.icon_id`, `rewards.icon_id`. `resolveIcon()` turns it into an icon.
- `components/TobiIcon.tsx` draws the round background and the image (`contain`);
  `components/TobiIconPicker.tsx` is the «Выбрать иконку» sheet.

## Add a new icon
1. Put the file here: `webp/<category>/<new_id>.webp` (square, transparent, symbol ≈70% of the canvas
   like the rest of the library; PNG also works).
2. Append an entry to `ICON_LIBRARY` with a **new unique id** and a literal path:
   `{ id: 'surfing', label: 'Сёрфинг', glyph: { kind: 'image', source: require('@/assets/icons/webp/sport/surfing.webp') }, color: 'sport' }`
3. `require(...)` must have a literal path — Metro does not support dynamic `require`.

## Replace an image without changing the id
Overwrite the file (same path) or point `source` to a new file. Keep the `id` — users keep their choice.

## Formats
PNG and WebP with an alpha channel (both supported by Expo on iOS and Android). Prefer WebP for size.

## Why ids must never change
The database keeps the id only. Renaming or reusing an id would silently change or lose the icon of
existing habits, goals and wishes. Removed ids are safe: they fall back to the default icon.

## Background color
`color` is a token from `iconColors` in `theme/colors.ts`. Library icons use their category token
(`sport`, `health`, `learning`, `work`, `finance`, `life` — values from `manifest.json`), because the
glyph colors are designed for these backgrounds. For a new category add a token there first.
