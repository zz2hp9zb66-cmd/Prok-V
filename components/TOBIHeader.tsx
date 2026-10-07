import { forwardRef } from 'react';
import { StyleSheet, View } from 'react-native';
import type { TobiState } from '@/features/tobi/states';
import { spacing } from '@/theme';
import { AppText } from './AppText';
import { PointsBadge } from './PointsBadge';
import { TOBIHero } from './TOBIHero';

export interface TOBIHeaderProps {
  tobiState: TobiState;
  title: string;
  subtitle?: string;
  balance: number;
}

/** TOBI Zone header: TOBI, greeting and balance (§18). Ref points at the balance badge. */
export const TOBIHeader = forwardRef<View, TOBIHeaderProps>(function TOBIHeader(
  { tobiState, title, subtitle, balance },
  balanceRef,
) {
  return (
    <View style={styles.container}>
      <TOBIHero state={tobiState} size={112} />
      <View style={styles.text}>
        <AppText variant="h2">{title}</AppText>
        {subtitle ? <AppText color="textSecondary">{subtitle}</AppText> : null}
        <PointsBadge ref={balanceRef} value={balance} size="lg" />
      </View>
    </View>
  );
});

const styles = StyleSheet.create({
  container: { flexDirection: 'row', alignItems: 'center', gap: spacing.sm },
  text: { flex: 1, gap: spacing.xs },
});
