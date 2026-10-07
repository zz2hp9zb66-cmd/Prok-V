import Ionicons from '@expo/vector-icons/Ionicons';
import type { ComponentProps } from 'react';
import { colors, type ColorToken, sizes } from '@/theme';

/** Only outline (rounded) Ionicons are used across the app (decision D9). */
export type IconName = Extract<ComponentProps<typeof Ionicons>['name'], `${string}-outline`>;

export interface IconProps {
  name: IconName;
  size?: number;
  color?: ColorToken;
  /** Raw color, e.g. from navigation tint. Prefer `color`. */
  tint?: string;
}

export function Icon({ name, size = sizes.iconMd, color = 'textPrimary', tint }: IconProps) {
  return <Ionicons name={name} size={size} color={tint ?? colors[color]} />;
}
