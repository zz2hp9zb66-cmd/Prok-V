import { forwardRef } from 'react';
import { StyleSheet, View } from 'react-native';
import { spacing } from '@/theme';
import { AppText } from './AppText';
import { PointsBadge } from './PointsBadge';

export interface TOBIHeaderProps {
  title: string;
  subtitle?: string;
  balance: number;
}

/**
 * Greeting + balance under TOBI's room (§18). TOBI himself is drawn in the
 * room header layer. Ref points at the balance badge (flying points target).
 */
export const TOBIHeader = forwardRef<View, TOBIHeaderProps>(function TOBIHeader({ title, subtitle, balance }, balanceRef) {
  return (
    <View style={styles.container}>
      <View style={styles.text}>
        <AppText variant="h2">{title}</AppText>
        {subtitle ? <AppText color="textSecondary">{subtitle}</AppText> : null}
      </View>
      <PointsBadge ref={balanceRef} value={balance} size="lg" />
    </View>
  );
});

const styles = StyleSheet.create({
  container: { flexDirection: 'row', alignItems: 'center', gap: spacing.sm },
  text: { flex: 1, gap: spacing.xxs },
});
