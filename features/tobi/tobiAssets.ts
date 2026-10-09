import type { ImageSourcePropType } from 'react-native';
import type { TobiState } from './states';

/** A static TOBI render: transparent PNG/WebP plus its pixel size (for proportions). */
export interface TobiRender {
  source: ImageSourcePropType;
  width: number;
  height: number;
  /**
   * Default placement in room headers (see `computeRoomCharacterFrame`):
   * scale 1 = from the status bar to the panel edge; offsetY as a share of the
   * character height (+ = lower part tucks behind the panel). Screen props override it.
   */
  placement?: { scale?: number; offsetX?: number; offsetY?: number };
}

/**
 * Registry of TOBI renders (§20). To connect a new render:
 *  1. put the transparent PNG/WebP into `assets/tobi/`;
 *  2. add one entry here: `tobi_tasks: { source: require('@/assets/tobi/tobi_tasks.png'), width: …, height: … }`.
 * Screens pick it up automatically; states without an entry show no character
 * in the room headers (and a neutral placeholder only in `TOBIHero`).
 */
export const tobiRenders: Partial<Record<TobiState, TobiRender>> = {
  // Product owner's render, unmodified (WebP with transparency).
  tobi_wave: { source: require('@/assets/tobi/tobi_wave.webp'), width: 1024, height: 1536 },
  // Product owner's render (PNG with transparency): thumbs up + plan notebook.
  tobi_habit_create: { source: require('@/assets/tobi/tobi_habit_create.png'), width: 1554, height: 1012 },
  // Product owner's render, unmodified (WebP with transparency): pencil + goal thought cloud.
  // 86% stays above the panel: cloud, pencil and both paws visible (paws end at ≈83%), pocket behind the panel.
  tobi_goal_create: {
    source: require('@/assets/tobi/tobi_goal_create.webp'),
    width: 1426,
    height: 1103,
    placement: { scale: 1 / 0.86, offsetY: 1 - 0.86 },
  },
  // Product owner's render, unmodified (WebP with transparency): dreaming TOBI with three thought clouds.
  // 84% stays above the panel: all clouds and both paws visible (they end at ≈78%), hoodie hem behind the panel.
  tobi_wish_create: {
    source: require('@/assets/tobi/tobi_wish_create.webp'),
    width: 1426,
    height: 1103,
    placement: { scale: 1 / 0.84, offsetY: 1 - 0.84 },
  },
};

/**
 * TOBI's shared room (§19: основная локация — комната TOBI). One file for the
 * headers of Задачи, Награды, Статистика and the goal / wish / task creation
 * screens. Original file from the product owner, unmodified (WebP, 1672×941).
 */
export const TOBI_ROOM_SHARED: ImageSourcePropType = require('@/assets/backgrounds/tobi_room_shared.webp');

/** Welcome screen scene (own approved design). Original file, unmodified (WebP, 853×1844). */
export const tobiScenes = {
  welcomeRoom: require('@/assets/tobi/welcome_room.webp') as ImageSourcePropType,
};
