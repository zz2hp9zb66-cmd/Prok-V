/** Radius scale — Design System §22: 8 / 12 / 16 / 24 / 32 / 999. */
export const radius = {
  xs: 8,
  sm: 12,
  md: 16,
  lg: 24,
  xl: 32,
  pill: 999,
} as const;

/** Component-level radii from §22 (cards 20–24, large panels 28–32). */
export const componentRadius = {
  card: radius.lg,
  panel: radius.xl,
  button: radius.pill,
} as const;

export type RadiusToken = keyof typeof radius;
