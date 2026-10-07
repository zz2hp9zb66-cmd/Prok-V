import { TextInput } from './TextInput';

export interface PointsInputProps {
  label: string;
  value: number | null;
  onChange: (value: number | null) => void;
  error?: string | null;
  placeholder?: string;
}

/** Positive integer input (points, cost, daily limit). No maximum (§8, §15). */
export function PointsInput({ label, value, onChange, error, placeholder }: PointsInputProps) {
  return (
    <TextInput
      label={label}
      error={error}
      placeholder={placeholder}
      keyboardType="number-pad"
      inputMode="numeric"
      value={value === null ? '' : String(value)}
      onChangeText={(text) => {
        const digits = text.replace(/\D/g, '');
        onChange(digits ? Number(digits) : null);
      }}
    />
  );
}
