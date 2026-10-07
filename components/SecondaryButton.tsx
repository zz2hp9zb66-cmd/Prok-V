import { Pressable, StyleSheet } from 'react-native';
import { colors, componentRadius, sizes, spacing } from '@/theme';
import { AppText } from './AppText';

export interface SecondaryButtonProps {
  title: string;
  onPress: () => void;
  disabled?: boolean;
  /** Destructive actions use the error color (D7). */
  tone?: 'default' | 'danger';
}

export function SecondaryButton({ title, onPress, disabled, tone = 'default' }: SecondaryButtonProps) {
  const color = disabled ? 'disabled' : tone === 'danger' ? 'error' : 'primary';
  return (
    <Pressable
      accessibilityRole="button"
      accessibilityState={{ disabled }}
      disabled={disabled}
      onPress={onPress}
      style={({ pressed }) => [styles.button, { borderColor: colors[color] }, pressed && styles.pressed]}
    >
      <AppText variant="button" color={color}>
        {title}
      </AppText>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  button: {
    minHeight: sizes.buttonHeight,
    borderRadius: componentRadius.button,
    borderWidth: 1.5,
    backgroundColor: colors.surface,
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: spacing.md,
  },
  pressed: { opacity: 0.7 },
});
