/** Spacing scale — Design System §22: 4 / 8 / 16 / 24 / 32 / 48 / 64. */
export const spacing = {
  xxs: 4,
  xs: 8,
  sm: 16,
  md: 24,
  lg: 32,
  xl: 48,
  xxl: 64,
} as const;

export type SpacingToken = keyof typeof spacing;
