import type { ReactNode } from 'react';
import { Pressable, StyleSheet, View, type StyleProp, type ViewStyle } from 'react-native';
import { colors, componentRadius, shadows, spacing } from '@/theme';

export interface CardProps {
  children: ReactNode;
  onPress?: () => void;
  muted?: boolean;
  style?: StyleProp<ViewStyle>;
  accessibilityLabel?: string;
}

/** White card with soft shadow (§22). `muted` = inactive state. */
export function Card({ children, onPress, muted, style, accessibilityLabel }: CardProps) {
  const content = [styles.card, muted && styles.muted, style];
  if (!onPress) return <View style={content}>{children}</View>;
  return (
    <Pressable
      accessibilityRole="button"
      accessibilityLabel={accessibilityLabel}
      onPress={onPress}
      style={({ pressed }) => [content, pressed && styles.pressed]}
    >
      {children}
    </Pressable>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: colors.surface,
    borderRadius: componentRadius.card,
    padding: spacing.sm,
    gap: spacing.xs,
    ...shadows.card,
  },
  muted: { backgroundColor: colors.surfaceMuted, borderWidth: 1, borderColor: colors.border, elevation: 0, shadowOpacity: 0 },
  pressed: { opacity: 0.9 },
});
