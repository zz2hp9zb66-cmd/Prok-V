import { Pressable, StyleSheet, View } from 'react-native';
import { colors, componentRadius, sizes, spacing } from '@/theme';
import { AppText } from './AppText';
import { Icon, type IconName } from './Icon';

export interface PrimaryButtonProps {
  title: string;
  onPress: () => void;
  disabled?: boolean;
  /** Icon at the right edge, e.g. an arrow for «Продолжить». */
  trailingIcon?: IconName;
}

/** Primary button (§22): orange, white text, 56–64 high, pill. */
export function PrimaryButton({ title, onPress, disabled, trailingIcon }: PrimaryButtonProps) {
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
      {trailingIcon ? (
        <View style={styles.trailing}>
          <Icon name={trailingIcon} color="textOnPrimary" />
        </View>
      ) : null}
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
  trailing: { position: 'absolute', right: spacing.md },
});
