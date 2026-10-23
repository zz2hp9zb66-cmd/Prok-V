import { Pressable, StyleSheet, View } from 'react-native';
import { colors, radius, spacing } from '@/theme';
import { AppText } from './AppText';
import { Icon } from './Icon';

export interface AddItemCardProps {
  title: string;
  onPress: () => void;
  testID?: string;
}

/**
 * Quiet secondary «Добавить …» card placed after the last item of a list
 * (habits, goals, wishes): round «+», action title, thin arrow. Part of the
 * scrolling content, never floating.
 */
export function AddItemCard({ title, onPress, testID }: AddItemCardProps) {
  return (
    <Pressable
      accessibilityRole="button"
      accessibilityLabel={title}
      onPress={onPress}
      testID={testID}
      style={({ pressed }) => [styles.card, pressed && styles.pressed]}
    >
      <View style={styles.plus}>
        <Icon name="add-outline" color="textPrimary" size={28} />
      </View>
      <AppText variant="bodyStrong" style={styles.title} numberOfLines={1}>
        {title}
      </AppText>
      <Icon name="chevron-forward-outline" color="textSecondary" size={22} />
    </Pressable>
  );
}

const styles = StyleSheet.create({
  card: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.sm - spacing.xxs,
    minHeight: 84,
    paddingLeft: spacing.sm,
    paddingRight: spacing.sm + spacing.xxs,
    borderRadius: radius.xl + spacing.xxs,
    backgroundColor: colors.addCard,
  },
  plus: {
    width: 52,
    height: 52,
    borderRadius: radius.pill,
    backgroundColor: colors.addCardIcon,
    alignItems: 'center',
    justifyContent: 'center',
  },
  title: { flex: 1, color: colors.textPrimary, opacity: 0.85, fontSize: 17 },
  pressed: { opacity: 0.75 },
});
