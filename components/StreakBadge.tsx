import { StyleSheet, View } from 'react-native';
import { formatDays } from '@/services/format';
import { colors, radius, spacing } from '@/theme';
import { AppText } from './AppText';
import { Icon } from './Icon';

export function StreakBadge({ days }: { days: number }) {
  return (
    <View style={styles.badge} accessibilityLabel={`Серия: ${formatDays(days)}`}>
      <Icon name="flame-outline" color="primary" />
      <AppText variant="h3">{formatDays(days)}</AppText>
      <AppText variant="caption" color="textSecondary">
        подряд
      </AppText>
    </View>
  );
}

const styles = StyleSheet.create({
  badge: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.xs,
    paddingVertical: spacing.xs,
    paddingHorizontal: spacing.sm,
    borderRadius: radius.pill,
    backgroundColor: colors.surface,
    alignSelf: 'flex-start',
  },
});
