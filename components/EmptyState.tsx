import { StyleSheet, View } from 'react-native';
import type { TobiState } from '@/features/tobi/states';
import { spacing } from '@/theme';
import { AppText } from './AppText';
import { PrimaryButton } from './PrimaryButton';
import { TOBIHero } from './TOBIHero';

export interface EmptyStateProps {
  title: string;
  description?: string;
  actionTitle?: string;
  onAction?: () => void;
  tobiState?: TobiState;
}

export function EmptyState({ title, description, actionTitle, onAction, tobiState }: EmptyStateProps) {
  return (
    <View style={styles.container}>
      {tobiState ? <TOBIHero state={tobiState} size={120} /> : null}
      <AppText variant="h3" align="center">
        {title}
      </AppText>
      {description ? (
        <AppText color="textSecondary" align="center">
          {description}
        </AppText>
      ) : null}
      {actionTitle && onAction ? <PrimaryButton title={actionTitle} onPress={onAction} /> : null}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { gap: spacing.sm, paddingVertical: spacing.lg, alignItems: 'stretch' },
});
