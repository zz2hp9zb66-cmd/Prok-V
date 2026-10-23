import { Pressable, StyleSheet, View, type GestureResponderEvent } from 'react-native';
import type { HabitDayView } from '@/features/habits/habitsService';
import { colors, radius, sizes, spacing } from '@/theme';
import { AppText } from './AppText';
import { Card } from './Card';
import { Icon } from './Icon';
import { TobiIcon } from './TobiIcon';

export interface HabitCardProps {
  view: HabitDayView;
  onPress: () => void;
  onComplete: (event: GestureResponderEvent) => void;
  busy?: boolean;
}

/**
 * Habit in the Tasks list (§18): icon, name + optional comment, checkbox,
 * points (and today's progress when the limit is above 1, §8), arrow to details.
 */
export function HabitCard({ view, onPress, onComplete, busy }: HabitCardProps) {
  const done = view.scheduledToday && !view.canComplete;
  const disabled = !view.canComplete || busy;
  const { name, comment } = view.habit;
  return (
    <Card muted={!view.scheduledToday} style={styles.card}>
      <View style={styles.row}>
        <Pressable
          accessibilityRole="button"
          accessibilityLabel={name}
          onPress={onPress}
          style={({ pressed }) => [styles.info, pressed && styles.pressed]}
        >
          <TobiIcon iconId={view.habit.iconId} owner="habit" size={sizes.touchTarget + spacing.xxs} />
          <View style={styles.text}>
            <AppText variant="cardTitle" color={view.scheduledToday ? 'textPrimary' : 'textSecondary'} numberOfLines={2}>
              {name}
            </AppText>
            {comment ? (
              <AppText variant="caption" color="textSecondary" numberOfLines={2}>
                {comment}
              </AppText>
            ) : null}
            {!view.scheduledToday ? (
              <AppText variant="small" color="textSecondary">
                Сегодня не запланирована
              </AppText>
            ) : null}
          </View>
        </Pressable>
        <Pressable
          accessibilityRole="checkbox"
          accessibilityLabel={`Выполнить: ${name}`}
          accessibilityState={{ checked: done, disabled }}
          disabled={disabled}
          onPress={onComplete}
          hitSlop={spacing.xxs}
          style={({ pressed }) => [styles.check, done && styles.checkDone, pressed && styles.pressed]}
        >
          {done ? <Icon name="checkmark-outline" color="textOnPrimary" size={sizes.iconMd + spacing.xxs} /> : null}
        </Pressable>
        <Pressable
          accessibilityRole="button"
          accessibilityLabel={`Подробнее: ${name}`}
          onPress={onPress}
          style={({ pressed }) => [styles.meta, pressed && styles.pressed]}
        >
          <View style={styles.points}>
            <AppText variant="bodyStrong" color={view.scheduledToday ? 'textPrimary' : 'textSecondary'}>
              +{view.pointsPerCompletion}
            </AppText>
            {view.scheduledToday && view.dailyLimit > 1 ? (
              <AppText variant="caption" color="textSecondary">
                {view.completedToday}/{view.dailyLimit}
              </AppText>
            ) : null}
          </View>
          <Icon name="chevron-forward-outline" color="primary" size={sizes.iconSm + spacing.xxs} />
        </Pressable>
      </View>
    </Card>
  );
}

const styles = StyleSheet.create({
  card: { paddingVertical: spacing.sm + spacing.xxs, paddingRight: spacing.xs },
  row: { flexDirection: 'row', alignItems: 'center', gap: spacing.xs },
  info: { flex: 1, flexDirection: 'row', alignItems: 'center', gap: spacing.sm - spacing.xxs },
  text: { flex: 1, gap: spacing.xxs / 2 },
  check: {
    width: sizes.touchTarget,
    height: sizes.touchTarget,
    borderRadius: radius.sm,
    borderWidth: 1.5,
    borderColor: colors.checkboxBorder,
    alignItems: 'center',
    justifyContent: 'center',
  },
  checkDone: { backgroundColor: colors.success, borderWidth: 0 },
  meta: { flexDirection: 'row', alignItems: 'center', gap: spacing.xxs, minHeight: sizes.touchTarget },
  points: { minWidth: sizes.touchTarget - spacing.xs, alignItems: 'flex-start' },
  pressed: { opacity: 0.85 },
});
