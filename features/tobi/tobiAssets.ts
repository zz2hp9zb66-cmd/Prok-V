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
 *  2. add one entry here: `tobi_reward: { source: require('@/assets/tobi/tobi_reward.png'), width: …, height: … }`.
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
  // 96% stays above the panel: all clouds, both paws and the hoodie visible; only the bottom edge touches the panel.
  tobi_wish_create: {
    source: require('@/assets/tobi/tobi_wish_create.webp'),
    width: 1426,
    height: 1103,
    placement: { scale: 1 / 0.96, offsetY: 1 - 0.96 },
  },
  // Product owner's render, unmodified (WebP with transparency): thumbs up, crown, heart speech cloud.
  // 86% stays above the panel: face, raised paw, crown, cloud, backpack straps and the hoodie visible.
  // The top 7% of the render is transparent, so it may sit in the status bar area: the crown starts under it.
  tobi_tasks: {
    source: require('@/assets/tobi/tobi_tasks.webp'),
    width: 1488,
    height: 1057,
    placement: { scale: 1 / (0.86 - 0.07), offsetY: 1 - 0.86 },
  },
  // Product owner's render, unmodified (WebP with transparency): golden star, heart cloud.
  // 84% stays above the panel: face, heart cloud and the whole star (ends at ≈80%) visible; hoodie behind the panel.
  // The top ≈2.7% of the render is transparent and may sit in the status bar area.
  tobi_rewards: {
    source: require('@/assets/tobi/tobi_rewards.webp'),
    width: 1569,
    height: 1002,
    placement: { scale: 1 / (0.84 - 0.027), offsetY: 1 - 0.84 },
  },
  // Product owner's render, unmodified (WebP with transparency): raised fist with orange strokes.
  // 86% stays above the panel: strokes, fist, face, backpack straps and the hoodie down to the pocket visible.
  tobi_statistics: {
    source: require('@/assets/tobi/tobi_statistics.webp'),
    width: 1575,
    height: 998,
    placement: { scale: 1 / 0.86, offsetY: 1 - 0.86 },
  },
  // Product owner's render, unmodified (WebP with transparency): full-height TOBI with pencil and notebook.
  // The whole character (alpha 4.9%…95.5% of the height) fits between the status bar and the panel;
  // only transparent margins extend beyond.
  tobi_reward_edit: {
    source: require('@/assets/tobi/tobi_reward_edit.webp'),
    width: 1024,
    height: 1536,
    placement: { scale: 1 / (0.955 - 0.049), offsetY: 1 - 0.955 },
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
