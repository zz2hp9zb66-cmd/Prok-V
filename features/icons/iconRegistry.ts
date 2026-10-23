import type { ComponentProps } from 'react';
import type Ionicons from '@expo/vector-icons/Ionicons';
import type { ImageSourcePropType } from 'react-native';
import type { IconColorToken } from '@/theme';

/** Which kind of item an icon belongs to (decides the default icon). */
export type IconOwner = 'habit' | 'goal' | 'wish';

type IoniconName = ComponentProps<typeof Ionicons>['name'];

/**
 * Where the glyph comes from:
 *  - `vector` — a temporary Ionicons glyph;
 *  - `image` — a local PNG/WebP with transparency from `assets/icons/`,
 *    registered with a static `require` (Metro needs literal paths).
 */
export type IconGlyph = { kind: 'vector'; name: IoniconName } | { kind: 'image'; source: ImageSourcePropType };

export interface TobiIconDef {
  /** Stable id stored in SQLite. Never rename or reuse an id. */
  id: string;
  /** Russian label shown to the user. */
  label: string;
  glyph: IconGlyph;
  /** Background circle + glyph tint (tint is ignored for full-color images). */
  color: IconColorToken;
}

/**
 * Icon library, in picker order. To replace a temporary glyph with an
 * authored image keep the id and change only `glyph`, e.g.
 *   glyph: { kind: 'image', source: require('@/assets/icons/sport.png') }
 * Users keep their choice because SQLite stores only the id.
 */
export const ICON_LIBRARY: readonly TobiIconDef[] = [
  { id: 'sport', label: 'Спорт', glyph: { kind: 'vector', name: 'walk-outline' }, color: 'green' },
  { id: 'reading', label: 'Чтение', glyph: { kind: 'vector', name: 'book-outline' }, color: 'peach' },
  { id: 'water', label: 'Вода', glyph: { kind: 'vector', name: 'water-outline' }, color: 'blue' },
  { id: 'language', label: 'Языки', glyph: { kind: 'vector', name: 'language-outline' }, color: 'violet' },
  { id: 'sleep', label: 'Сон', glyph: { kind: 'vector', name: 'moon-outline' }, color: 'lilac' },
];

/** Universal per-type icons: used when nothing was chosen or the id is unknown. */
export const DEFAULT_ICONS: Readonly<Record<IconOwner, TobiIconDef>> = {
  habit: { id: 'default_habit', label: 'Привычка', glyph: { kind: 'vector', name: 'checkmark-done-outline' }, color: 'amber' },
  goal: { id: 'default_goal', label: 'Цель', glyph: { kind: 'vector', name: 'flag-outline' }, color: 'peach' },
  wish: { id: 'default_wish', label: 'Желание', glyph: { kind: 'vector', name: 'gift-outline' }, color: 'rose' },
};

const BY_ID = new Map<string, TobiIconDef>(
  [...ICON_LIBRARY, ...Object.values(DEFAULT_ICONS)].map((icon) => [icon.id, icon]),
);

/** Icons offered in the picker for an item type: its default first, then the library. */
export function pickerIcons(owner: IconOwner): TobiIconDef[] {
  return [DEFAULT_ICONS[owner], ...ICON_LIBRARY];
}

/** Resolves a stored id; null/unknown ids fall back to the type's default (never throws). */
export function resolveIcon(iconId: string | null | undefined, owner: IconOwner): TobiIconDef {
  return (iconId && BY_ID.get(iconId)) || DEFAULT_ICONS[owner];
}

export function defaultIconId(owner: IconOwner): string {
  return DEFAULT_ICONS[owner].id;
}
