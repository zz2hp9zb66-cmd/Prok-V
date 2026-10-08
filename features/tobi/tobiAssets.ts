import type { ImageSourcePropType } from 'react-native';
import type { TobiState } from './states';

/**
 * Registry of TOBI renders. Empty until the product owner provides the
 * assets; components fall back to a neutral placeholder meanwhile.
 * Animation file format is decided after testing the first real animation (§20).
 */
export const tobiImages: Partial<Record<TobiState, ImageSourcePropType>> = {};

/**
 * Full-screen TOBI locations (§19: основная локация — комната TOBI).
 * `null` until the file is added to `assets/tobi/`; screens then fall back
 * to the plain cream background.
 */
export const tobiScenes: { welcomeRoom: ImageSourcePropType | null } = {
  // Original file from the product owner, unmodified (WebP, 853×1844).
  welcomeRoom: require('@/assets/tobi/welcome_room.webp'),
};
