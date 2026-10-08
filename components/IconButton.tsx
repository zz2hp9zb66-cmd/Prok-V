import { Pressable, StyleSheet } from 'react-native';
import { colors, radius, shadows, sizes } from '@/theme';
import { Icon, type IconName } from './Icon';

export interface IconButtonProps {
  icon: IconName;
  onPress: () => void;
  accessibilityLabel: string;
  disabled?: boolean;
  /** `surface` = white round button over images (e.g. back). */
  tone?: 'primary' | 'surface';
}

/** Round primary icon button (e.g. contextual `+`). */
export function IconButton({ icon, onPress, accessibilityLabel, disabled, tone = 'primary' }: IconButtonProps) {
  const surface = tone === 'surface';
  return (
    <Pressable
      accessibilityRole="button"
      accessibilityLabel={accessibilityLabel}
      accessibilityState={{ disabled }}
      disabled={disabled}
      onPress={onPress}
      hitSlop={8}
      style={({ pressed }) => [styles.button, surface && styles.surface, disabled && styles.disabled, pressed && styles.pressed]}
    >
      <Icon name={icon} color={surface ? 'textPrimary' : 'textOnPrimary'} />
    </Pressable>
  );
}

const styles = StyleSheet.create({
  button: {
    width: sizes.touchTarget,
    height: sizes.touchTarget,
    borderRadius: radius.pill,
    backgroundColor: colors.primary,
    alignItems: 'center',
    justifyContent: 'center',
  },
  surface: { backgroundColor: colors.surface, ...shadows.card },
  disabled: { backgroundColor: colors.disabled },
  pressed: { opacity: 0.85 },
});
