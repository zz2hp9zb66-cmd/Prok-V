import { StyleSheet, View } from 'react-native';
import { spacing } from '@/theme';
import { AppText } from './AppText';
import { IconButton } from './IconButton';

export interface SectionHeaderProps {
  title: string;
  /** Contextual create action (§6). */
  onAdd?: () => void;
  addLabel?: string;
}

export function SectionHeader({ title, onAdd, addLabel = 'Создать' }: SectionHeaderProps) {
  return (
    <View style={styles.row}>
      <AppText variant="h2" style={styles.title}>
        {title}
      </AppText>
      {onAdd ? <IconButton icon="add-outline" onPress={onAdd} accessibilityLabel={addLabel} /> : null}
    </View>
  );
}

const styles = StyleSheet.create({
  row: { flexDirection: 'row', alignItems: 'center', gap: spacing.xs, minHeight: 44 },
  title: { flex: 1 },
});
