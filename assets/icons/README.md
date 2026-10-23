# Item icons (habits, goals, wishes)

Authored icon images for TOBI Habit: PNG or WebP, transparent background, no text,
one visual style, stored locally (no network).

## How to add or replace an icon
1. Put the file here, e.g. `assets/icons/sport.png` (square, ~256×256 is enough).
2. In `features/icons/iconRegistry.ts`:
   - **replace a temporary glyph** — keep the `id`, change only `glyph`:
     `{ id: 'sport', label: 'Спорт', glyph: { kind: 'image', source: require('@/assets/icons/sport.png') }, color: 'green' }`
   - **add a new icon** — append a new entry with a new unique `id` to `ICON_LIBRARY`.
3. Use a literal path in `require(...)` (Metro does not support dynamic `require`).

Never rename or reuse an `id`: SQLite stores only the id (`habits.icon_id`, `rewards.icon_id`).
Unknown or removed ids fall back to the default icon of the item type.
Background colors come from `iconColors` in `theme/colors.ts`.
