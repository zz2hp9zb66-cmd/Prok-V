import { Pressable, StyleSheet } from 'react-native';
import { colors, componentRadius, sizes, spacing } from '@/theme';
import { AppText } from './AppText';

export interface PrimaryButtonProps {
  title: string;
  onPress: () => void;
  disabled?: boolean;
}

/** Primary button (§22): orange, white text, 56–64 high, pill. */
export function PrimaryButton({ title, onPress, disabled }: PrimaryButtonProps) {
  return (
    <Pressable
      accessibilityRole="button"
      accessibilityState={{ disabled }}
      disabled={disabled}
      onPress={onPress}
      style={({ pressed }) => [styles.button, disabled && styles.disabled, pressed && styles.pressed]}
    >
      <AppText variant="button" color="textOnPrimary">
        {title}
      </AppText>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  button: {
    minHeight: sizes.buttonHeight,
    borderRadius: componentRadius.button,
    backgroundColor: colors.primary,
    alignItems: 'center',
    justifyContent: 'center',
    paddingHorizontal: spacing.md,
  },
  disabled: { backgroundColor: colors.disabled },
  pressed: { opacity: 0.85 },
});
