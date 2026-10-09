import type { ImageSourcePropType } from 'react-native';
import type { TobiState } from './states';

/**
 * Registry of TOBI renders. Empty until the product owner provides the
 * assets; components fall back to a neutral placeholder meanwhile.
 * Animation file format is decided after testing the first real animation (§20).
 */
export const tobiImages: Partial<Record<TobiState, ImageSourcePropType>> = {
  // Product owner's render, unmodified (WebP with transparency, 1024×1536).
  tobi_wave: require('@/assets/tobi/tobi_wave.webp'),
  // Product owner's render (PNG with transparency, 1554×1012): thumbs up + plan notebook.
  tobi_habit_create: require('@/assets/tobi/tobi_habit_create.png'),
};

/**
 * Full-screen TOBI locations (§19: основная локация — комната TOBI).
 * `null` until the file is added to `assets/tobi/`; screens then fall back
 * to the plain cream background.
 */
const welcomeRoom: ImageSourcePropType = require('@/assets/tobi/welcome_room.webp');

export const tobiScenes: { welcomeRoom: ImageSourcePropType | null; taskCreateRoom: ImageSourcePropType | null } = {
  // Original file from the product owner, unmodified (WebP, 853×1844).
  welcomeRoom,
  // Task creation header. Uses TOBI's room until a dedicated scene is provided.
  taskCreateRoom: welcomeRoom,
};
