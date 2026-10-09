/**
 * Placement of the `tobi_habit_create` render in the task creation header,
 * computed from the screen (no fixed coordinates):
 *  - ears start just under the status bar, so the head is never cut;
 *  - the render stands on the cream panel: only the hoodie hem (below the
 *    notebook) goes behind the panel's rounded top, the notebook stays visible;
 *  - horizontally centred, at most 96% of the screen width.
 */

/** Render aspect ratio (1554×1012, width / height). */
export const TOBI_HABIT_CREATE_ASPECT = 1554 / 1012;
/** Share of the render height that must stay visible (notebook ends at ≈94%). */
const VISIBLE_SHARE = 0.955;
const MAX_WIDTH_SHARE = 0.96;
const GAP_UNDER_STATUS_BAR = 4;

export interface TaskCreateTobiInput {
  screenWidth: number;
  /** Safe area top inset (status bar / Dynamic Island). */
  insetTop: number;
  /** Y of the panel's top edge inside the header (header height minus panel overlap). */
  panelTop: number;
}

export interface TaskCreateTobiFrame {
  left: number;
  top: number;
  width: number;
  height: number;
}

export function computeTaskCreateTobiFrame({ screenWidth, insetTop, panelTop }: TaskCreateTobiInput): TaskCreateTobiFrame {
  const topLimit = insetTop + GAP_UNDER_STATUS_BAR;
  const height = Math.max(
    0,
    Math.min((panelTop - topLimit) / VISIBLE_SHARE, (screenWidth * MAX_WIDTH_SHARE) / TOBI_HABIT_CREATE_ASPECT),
  );
  const width = height * TOBI_HABIT_CREATE_ASPECT;
  return { left: (screenWidth - width) / 2, top: panelTop - height * VISIBLE_SHARE, width, height };
}
