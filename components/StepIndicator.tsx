import { StyleSheet, View } from 'react-native';
import { spacing } from '@/theme';
import { AppText } from './AppText';
import { ProgressBar } from './ProgressBar';

/** «2/3» + progress bar for multi-step flows (onboarding). */
export function StepIndicator({ step, total }: { step: number; total: number }) {
  return (
    <View style={styles.row} accessibilityLabel={`Шаг ${step} из ${total}`}>
      <AppText variant="bodyStrong">
        {step}/{total}
      </AppText>
      <View style={styles.bar}>
        <ProgressBar progress={step / total} />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  row: { flexDirection: 'row', alignItems: 'center', gap: spacing.sm },
  bar: { flex: 1 },
});
