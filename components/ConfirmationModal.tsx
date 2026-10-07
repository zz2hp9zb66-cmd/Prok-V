import { Modal, Pressable, StyleSheet, View } from 'react-native';
import { colors, componentRadius, shadows, spacing } from '@/theme';
import { AppText } from './AppText';
import { PrimaryButton } from './PrimaryButton';
import { SecondaryButton } from './SecondaryButton';

export interface ConfirmationModalProps {
  visible: boolean;
  title: string;
  message?: string;
  confirmTitle: string;
  cancelTitle?: string;
  destructive?: boolean;
  onConfirm: () => void;
  onCancel: () => void;
}

/** Bottom sheet confirmation (used for deletions, §11). */
export function ConfirmationModal({
  visible,
  title,
  message,
  confirmTitle,
  cancelTitle = 'Отмена',
  destructive,
  onConfirm,
  onCancel,
}: ConfirmationModalProps) {
  return (
    <Modal visible={visible} transparent animationType="slide" onRequestClose={onCancel}>
      <Pressable style={styles.backdrop} onPress={onCancel} accessibilityLabel={cancelTitle} />
      <View style={styles.sheet}>
        <AppText variant="h3">{title}</AppText>
        {message ? <AppText color="textSecondary">{message}</AppText> : null}
        {destructive ? (
          <SecondaryButton title={confirmTitle} tone="danger" onPress={onConfirm} />
        ) : (
          <PrimaryButton title={confirmTitle} onPress={onConfirm} />
        )}
        <SecondaryButton title={cancelTitle} onPress={onCancel} />
      </View>
    </Modal>
  );
}

const styles = StyleSheet.create({
  backdrop: { flex: 1, backgroundColor: colors.overlay },
  sheet: {
    backgroundColor: colors.background,
    borderTopLeftRadius: componentRadius.panel,
    borderTopRightRadius: componentRadius.panel,
    padding: spacing.md,
    paddingBottom: spacing.xl,
    gap: spacing.sm,
    ...shadows.panel,
  },
});
