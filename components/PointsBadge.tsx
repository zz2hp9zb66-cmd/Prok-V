import { forwardRef } from 'react';
import { StyleSheet, View } from 'react-native';
import { formatPoints } from '@/services/format';
import { colors, radius, spacing } from '@/theme';
import { AppText } from './AppText';
import { Icon } from './Icon';

export interface PointsBadgeProps {
  value: number;
  size?: 'md' | 'lg';
}

/** Balance / points pill. Forwarded ref lets animations measure its position. */
export const PointsBadge = forwardRef<View, PointsBadgeProps>(function PointsBadge({ value, size = 'md' }, ref) {
  return (
    <View ref={ref} style={styles.badge} accessibilityLabel={`Баланс: ${formatPoints(value)}`}>
      <Icon name="star-outline" color="accentDark" size={size === 'lg' ? 22 : 18} />
      <AppText variant={size === 'lg' ? 'h3' : 'bodyStrong'} color="accentDark">
        {formatPoints(value)}
      </AppText>
    </View>
  );
});

const styles = StyleSheet.create({
  badge: {
    flexDirection: 'row',
    alignItems: 'center',
    alignSelf: 'flex-start',
    gap: spacing.xxs,
    paddingVertical: spacing.xxs,
    paddingHorizontal: spacing.sm,
    borderRadius: radius.pill,
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.primarySoft,
  },
});
