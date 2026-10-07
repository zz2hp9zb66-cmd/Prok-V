import type { ImageSourcePropType } from 'react-native';
import type { TobiState } from './states';

/**
 * Registry of TOBI renders. Empty until the product owner provides the
 * assets; components fall back to a neutral placeholder meanwhile.
 * Animation file format is decided after testing the first real animation (§20).
 */
export const tobiImages: Partial<Record<TobiState, ImageSourcePropType>> = {};
