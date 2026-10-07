import { StyleSheet, View } from 'react-native';
import { WEEKDAY_LONG, WEEKDAY_SHORT } from '@/services/format';
import { WEEKDAYS, type Weekday } from '@/services/time';
import { spacing } from '@/theme';
import { FilterChip } from './FilterChip';

export interface DaySelectorProps {
  value: readonly Weekday[];
  onChange: (days: Weekday[]) => void;
}

/** ПН–ВС selector (§7). */
export function DaySelector({ value, onChange }: DaySelectorProps) {
  const toggle = (day: Weekday) =>
    onChange(value.includes(day) ? value.filter((d) => d !== day) : WEEKDAYS.filter((d) => d === day || value.includes(d)));
  return (
    <View style={styles.row}>
      {WEEKDAYS.map((day) => (
        <FilterChip
          key={day}
          label={WEEKDAY_SHORT[day]}
          accessibilityLabel={WEEKDAY_LONG[day]}
          selected={value.includes(day)}
          onPress={() => toggle(day)}
        />
      ))}
    </View>
  );
}

const styles = StyleSheet.create({
  row: { flexDirection: 'row', flexWrap: 'wrap', justifyContent: 'space-between', gap: spacing.xxs },
});
