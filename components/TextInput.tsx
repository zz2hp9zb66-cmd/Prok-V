import { TextInput as RNTextInput, StyleSheet, View, type TextInputProps as RNTextInputProps } from 'react-native';
import { colors, radius, spacing, typography } from '@/theme';
import { AppText } from './AppText';

export interface TextInputProps extends Omit<RNTextInputProps, 'style'> {
  label: string;
  error?: string | null;
}

export function TextInput({ label, error, ...rest }: TextInputProps) {
  return (
    <View style={styles.field}>
      <AppText variant="caption" color="textSecondary">
        {label}
      </AppText>
      <RNTextInput
        accessibilityLabel={label}
        placeholderTextColor={colors.textSecondary}
        style={[styles.input, error ? styles.inputError : null]}
        {...rest}
      />
      {error ? (
        <AppText variant="small" color="error">
          {error}
        </AppText>
      ) : null}
    </View>
  );
}

const styles = StyleSheet.create({
  field: { gap: spacing.xxs },
  input: {
    ...typography.body,
    color: colors.textPrimary,
    backgroundColor: colors.surface,
    borderRadius: radius.md,
    borderWidth: 1,
    borderColor: colors.border,
    paddingHorizontal: spacing.sm,
    minHeight: 52,
  },
  inputError: { borderColor: colors.error },
});
