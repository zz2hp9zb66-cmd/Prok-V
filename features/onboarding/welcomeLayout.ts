/**
 * Adaptive placement of TOBI on the welcome screen, derived from the approved
 * reference (proportions of the screen, not fixed coordinates):
 *  - TOBI is ~51% of the screen height tall, feet at ~76% of the height,
 *  - the character's centre sits slightly left of the screen centre so the
 *    body/head read slightly right of centre (the tail extends to the left),
 *  - never overlaps the title block, never reaches the «Начать» button.
 */

/** Visible character inside the `tobi_wave` render (alpha bounds, as fractions of the 2:3 image). */
export const TOBI_WAVE_BOUNDS = { left: 0.011, right: 0.993, top: 0.066, bottom: 0.949 } as const;
/** Render aspect ratio (width / height). */
export const TOBI_WAVE_ASPECT = 2 / 3;

const TARGET_CHARACTER_HEIGHT = 0.515; // of screen height
const TARGET_FEET = 0.77; // of screen height
const GAP_ABOVE_BUTTON = 0.04; // of screen height, between feet and button
const GAP_BELOW_TEXT = 0.015; // of screen height, between text and ears
const MAX_CHARACTER_WIDTH = 0.92; // of screen width
const CHARACTER_CENTER_X = 0.47; // of screen width

export interface WelcomeLayoutInput {
  width: number;
  height: number;
  /** Bottom edge of the title + subtitle block. */
  textBottom: number;
  /** Top edge of the «Начать» button. */
  buttonTop: number;
}

export interface TobiFrame {
  /** Image box (the whole 2:3 render, `contain`). */
  left: number;
  top: number;
  width: number;
  height: number;
}

export function computeTobiFrame({ width, height, textBottom, buttonTop }: WelcomeLayoutInput): TobiFrame {
  const b = TOBI_WAVE_BOUNDS;
  const charHeightShare = b.bottom - b.top;
  const charWidthShare = (b.right - b.left) * TOBI_WAVE_ASPECT;

  const feet = Math.min(height * TARGET_FEET, buttonTop - height * GAP_ABOVE_BUTTON);
  const minEarsY = textBottom + height * GAP_BELOW_TEXT;

  const boxHeight = Math.max(
    0,
    Math.min(
      (height * TARGET_CHARACTER_HEIGHT) / charHeightShare,
      (feet - minEarsY) / charHeightShare,
      (width * MAX_CHARACTER_WIDTH) / charWidthShare,
    ),
  );
  const boxWidth = boxHeight * TOBI_WAVE_ASPECT;
  const top = feet - boxHeight * b.bottom;

  const charWidth = boxHeight * charWidthShare;
  const charLeftEdge = boxWidth * b.left;
  // Centre the visible character at CHARACTER_CENTER_X, keeping the tail and ear on screen.
  let left = width * CHARACTER_CENTER_X - charWidth / 2 - charLeftEdge;
  left = Math.max(left, -charLeftEdge);
  left = Math.min(left, width - boxWidth * b.right);

  return { left, top, width: boxWidth, height: boxHeight };
}
