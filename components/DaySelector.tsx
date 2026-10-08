import { Pressable, StyleSheet, View } from 'react-native';
import { WEEKDAY_LONG, WEEKDAY_TITLE } from '@/services/format';
import { WEEKDAYS, type Weekday } from '@/services/time';
import { colors, radius, sizes, spacing } from '@/theme';
import { AppText } from './AppText';

export interface DaySelectorProps {
  value: readonly Weekday[];
  onChange: (days: Weekday[]) => void;
}

/** Пн–Вс in one row; each day toggles independently (§7). Selected days are orange. */
export function DaySelector({ value, onChange }: DaySelectorProps) {
  const toggle = (day: Weekday) =>
    onChange(value.includes(day) ? value.filter((d) => d !== day) : WEEKDAYS.filter((d) => d === day || value.includes(d)));
  return (
    <View style={styles.row}>
      {WEEKDAYS.map((day) => {
        const selected = value.includes(day);
        return (
          <Pressable
            key={day}
            accessibilityRole="checkbox"
            accessibilityState={{ checked: selected }}
            accessibilityLabel={WEEKDAY_LONG[day]}
            onPress={() => toggle(day)}
            style={({ pressed }) => [styles.day, selected ? styles.selected : styles.unselected, pressed && styles.pressed]}
          >
            <AppText variant="bodyStrong" color={selected ? 'textOnPrimary' : 'primary'}>
              {WEEKDAY_TITLE[day]}
            </AppText>
          </Pressable>
        );
      })}
    </View>
  );
}

const styles = StyleSheet.create({
  row: { flexDirection: 'row', gap: spacing.xxs + 2 },
  day: {
    flex: 1,
    minHeight: sizes.touchTarget,
    aspectRatio: 1,
    maxHeight: 56,
    borderRadius: radius.md,
    borderWidth: 1.5,
    alignItems: 'center',
    justifyContent: 'center',
  },
  selected: { backgroundColor: colors.primary, borderColor: colors.primary },
  unselected: { backgroundColor: colors.surface, borderColor: colors.primarySoft },
  pressed: { opacity: 0.85 },
});
