import type { ReactNode } from 'react';
import { TextInput as RNTextInput, StyleSheet, View, type TextInputProps as RNTextInputProps } from 'react-native';
import { colors, radius, spacing, typography } from '@/theme';
import { AppText } from './AppText';

export interface TextInputProps extends Omit<RNTextInputProps, 'style'> {
  label: string;
  error?: string | null;
  /** `heading` = bold field title (task creation design), `caption` = small grey label. */
  labelVariant?: 'caption' | 'heading';
  /** Element next to the label, e.g. a help button. */
  labelAccessory?: ReactNode;
  /** Element inside the field before the text, e.g. an icon. */
  leading?: ReactNode;
  /** Shows «n/maxLength» under the field. Requires `maxLength`. */
  showCounter?: boolean;
  /** Neutral helper text under the field (hidden while an error is shown). */
  hint?: string | null;
}

export function TextInput({
  label,
  error,
  labelVariant = 'caption',
  labelAccessory,
  leading,
  showCounter,
  hint,
  value,
  maxLength,
  ...rest
}: TextInputProps) {
  const heading = labelVariant === 'heading';
  const counter = showCounter && maxLength !== undefined ? `${value?.length ?? 0}/${maxLength}` : null;
  return (
    <View style={styles.field}>
      <View style={styles.labelRow}>
        <AppText variant={heading ? 'h3' : 'caption'} color={heading ? 'textPrimary' : 'textSecondary'}>
          {label}
        </AppText>
        {labelAccessory}
      </View>
      {hint && !error ? (
        <AppText variant="caption" color="textSecondary">
          {hint}
        </AppText>
      ) : null}
      <View style={[styles.box, heading && styles.boxLarge, leading ? styles.boxWithLeading : null, error ? styles.boxError : null]}>
        {leading}
        <RNTextInput
          accessibilityLabel={label}
          placeholderTextColor={colors.textSecondary}
          style={styles.input}
          value={value}
          maxLength={maxLength}
          {...rest}
        />
      </View>
      {error || counter ? (
        <View style={styles.footer}>
          <AppText variant="small" color="error" style={styles.footerText}>
            {error ?? ''}
          </AppText>
          {counter ? (
            <AppText variant="small" color="textSecondary" accessibilityLabel={`Символов: ${counter}`}>
              {counter}
            </AppText>
          ) : null}
        </View>
      ) : null}
    </View>
  );
}

const styles = StyleSheet.create({
  field: { gap: spacing.xxs },
  labelRow: { flexDirection: 'row', alignItems: 'center', gap: spacing.xs },
  box: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.xs,
    backgroundColor: colors.surface,
    borderRadius: radius.md,
    borderWidth: 1,
    borderColor: colors.border,
    paddingHorizontal: spacing.sm,
    minHeight: 52,
  },
  boxLarge: { borderRadius: radius.lg, minHeight: 56, paddingLeft: spacing.sm },
  boxWithLeading: { paddingLeft: spacing.xs, paddingRight: spacing.sm - spacing.xxs },
  boxError: { borderColor: colors.error },
  input: { ...typography.body, flex: 1, color: colors.textPrimary, minHeight: 48 },
  footer: { flexDirection: 'row', gap: spacing.xs },
  footerText: { flex: 1 },
});
