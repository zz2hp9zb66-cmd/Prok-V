import type { TextStyle } from 'react-native';

/** Typography scale — Design System §22 (values picked inside the spec ranges). */
export const typography = {
  display: { fontSize: 44, lineHeight: 52, fontWeight: '700' },
  h1: { fontSize: 32, lineHeight: 40, fontWeight: '700' },
  h2: { fontSize: 26, lineHeight: 32, fontWeight: '700' },
  h3: { fontSize: 20, lineHeight: 26, fontWeight: '600' },
  /** Lead paragraph under a display title (welcome screen). */
  lead: { fontSize: 17, lineHeight: 24, fontWeight: '500' },
  body: { fontSize: 16, lineHeight: 22, fontWeight: '400' },
  bodyStrong: { fontSize: 16, lineHeight: 22, fontWeight: '600' },
  caption: { fontSize: 14, lineHeight: 18, fontWeight: '400' },
  small: { fontSize: 12, lineHeight: 16, fontWeight: '400' },
  button: { fontSize: 18, lineHeight: 22, fontWeight: '600' },
} as const satisfies Record<string, TextStyle>;

export type TypographyToken = keyof typeof typography;
