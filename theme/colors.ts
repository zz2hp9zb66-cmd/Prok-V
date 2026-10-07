/**
 * Color tokens — Design System §22.
 * Brand and neutral values are approved by the spec.
 * Functional (success/warning/error/info) values are PROVISIONAL: the spec
 * requires them to be centralized but does not define them.
 */
export const palette = {
  brand: {
    orange: '#E76F2E',
    orangeLight: '#F4B070',
    amber: '#FFB347',
    brown: '#8B5A3C',
  },
  neutral: {
    white: '#FFFFFF',
    cream: '#FFF9F3',
    black: '#2E2E2E',
    gray: '#6B6B6B',
    lightGray: '#D4D4D4',
  },
  functional: {
    success: '#4CAF7A',
    warning: '#FFB347',
    error: '#D9534F',
    info: '#4A90C2',
  },
} as const;

/** Semantic aliases used by components and screens. */
export const colors = {
  background: palette.neutral.cream,
  surface: palette.neutral.white,
  surfaceMuted: palette.neutral.cream,
  border: palette.neutral.lightGray,
  textPrimary: palette.neutral.black,
  textSecondary: palette.neutral.gray,
  textOnPrimary: palette.neutral.white,
  primary: palette.brand.orange,
  primarySoft: palette.brand.orangeLight,
  accent: palette.brand.amber,
  accentDark: palette.brand.brown,
  disabled: palette.neutral.lightGray,
  shadow: palette.brand.brown,
  ...palette.functional,
} as const;

export type ColorToken = keyof typeof colors;
