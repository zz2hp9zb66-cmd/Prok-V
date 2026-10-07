import { Pressable, StyleSheet, View, type GestureResponderEvent } from 'react-native';
import type { HabitDayView } from '@/features/habits/habitsService';
import { formatPoints } from '@/services/format';
import { colors, radius, sizes, spacing } from '@/theme';
import { AppText } from './AppText';
import { Card } from './Card';
import { Icon } from './Icon';
import { ProgressBar } from './ProgressBar';

export interface HabitCardProps {
  view: HabitDayView;
  onPress: () => void;
  onComplete: (event: GestureResponderEvent) => void;
  busy?: boolean;
}

function statusText(view: HabitDayView): string {
  if (!view.scheduledToday) return 'Сегодня не запланирована';
  if (!view.canComplete) return 'На сегодня выполнено';
  return `+${formatPoints(view.pointsPerCompletion)}`;
}

/** Habit in the Tasks list: progress, points and the complete action (§18). */
export function HabitCard({ view, onPress, onComplete, busy }: HabitCardProps) {
  const disabled = !view.canComplete || busy;
  const inactive = !view.canComplete;
  return (
    <Card muted={inactive}>
      <View style={styles.row}>
        <Pressable
          accessibilityRole="button"
          accessibilityLabel={view.habit.name}
          onPress={onPress}
          style={({ pressed }) => [styles.info, pressed && styles.pressed]}
        >
          <AppText variant="h3" color={inactive ? 'textSecondary' : 'textPrimary'} numberOfLines={2}>
            {view.habit.name}
          </AppText>
          <AppText variant="caption" color={view.scheduledToday && view.canComplete ? 'accentDark' : 'textSecondary'}>
            {statusText(view)}
          </AppText>
          {view.scheduledToday ? (
            <View style={styles.progress}>
              <View style={styles.bar}>
                <ProgressBar progress={view.completedToday / view.dailyLimit} color={inactive ? 'success' : 'primary'} />
              </View>
              <AppText variant="caption" color="textSecondary">
                {view.completedToday}/{view.dailyLimit}
              </AppText>
            </View>
          ) : null}
        </Pressable>
        <Pressable
          accessibilityRole="button"
          accessibilityLabel={`Выполнить: ${view.habit.name}`}
          accessibilityState={{ disabled }}
          disabled={disabled}
          onPress={onComplete}
          hitSlop={8}
          style={({ pressed }) => [styles.check, disabled && styles.checkDisabled, pressed && styles.pressed]}
        >
          <Icon name="checkmark-outline" color={disabled ? 'textSecondary' : 'textOnPrimary'} size={sizes.iconLg} />
        </Pressable>
      </View>
    </Card>
  );
}

const styles = StyleSheet.create({
  row: { flexDirection: 'row', alignItems: 'center', gap: spacing.sm },
  info: { flex: 1, gap: spacing.xxs },
  check: {
    width: 52,
    height: 52,
    borderRadius: radius.pill,
    backgroundColor: colors.primary,
    alignItems: 'center',
    justifyContent: 'center',
  },
  checkDisabled: { backgroundColor: colors.border },
  pressed: { opacity: 0.85 },
  progress: { flexDirection: 'row', alignItems: 'center', gap: spacing.xs, paddingTop: spacing.xxs },
  bar: { flex: 1 },
});
