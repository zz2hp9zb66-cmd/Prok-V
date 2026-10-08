import type { ReactNode } from 'react';
import { StyleSheet, View } from 'react-native';
import { colors, radius } from '@/theme';
import { Icon } from './Icon';
import { TextInput } from './TextInput';

/**
 * 15 digits always fit a JS safe integer and SQLite INTEGER. This is a
 * technical bound only; business rules have no maximum (§8, §15).
 */
const MAX_DIGITS = 15;

export interface PointsInputProps {
  label: string;
  value: number | null;
  onChange: (value: number | null) => void;
  error?: string | null;
  placeholder?: string;
  labelVariant?: 'caption' | 'heading';
  labelAccessory?: ReactNode;
  hint?: string | null;
  /** Star badge inside the field (points). */
  withStar?: boolean;
}

/** Positive integer input (points, cost, daily limit): digits only, number pad. */
export function PointsInput({ value, onChange, withStar, ...rest }: PointsInputProps) {
  return (
    <TextInput
      {...rest}
      keyboardType="number-pad"
      inputMode="numeric"
      maxLength={MAX_DIGITS}
      leading={
        withStar ? (
          <View style={styles.star}>
            <Icon name="star-outline" color="primary" size={20} />
          </View>
        ) : undefined
      }
      value={value === null ? '' : String(value)}
      onChangeText={(text) => {
        const digits = text.replace(/\D/g, '');
        onChange(digits ? Number(digits) : null);
      }}
    />
  );
}

const styles = StyleSheet.create({
  star: {
    width: 36,
    height: 36,
    borderRadius: radius.pill,
    backgroundColor: colors.surfaceMuted,
    borderWidth: 1,
    borderColor: colors.primarySoft,
    alignItems: 'center',
    justifyContent: 'center',
  },
});
