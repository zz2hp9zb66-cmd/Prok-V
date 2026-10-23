import { useState } from 'react';
import { Modal, Pressable, StyleSheet, View } from 'react-native';
import { type IconOwner, pickerIcons, resolveIcon } from '@/features/icons/iconRegistry';
import { colors, componentRadius, radius, shadows, spacing } from '@/theme';
import { AppText } from './AppText';
import { Icon } from './Icon';
import { PrimaryButton } from './PrimaryButton';
import { TobiIcon } from './TobiIcon';

export interface TobiIconPickerProps {
  owner: IconOwner;
  /** Current icon id; null = the type's default. */
  value: string | null;
  onChange: (iconId: string) => void;
  /** `heading` matches the bold field titles of the task creation design. */
  labelVariant?: 'caption' | 'heading';
}

/**
 * «Иконка» field (design reference): label, chevron and the current icon on the
 * right; tapping opens «Выбрать иконку» with a 3-column grid. «Выбрать» applies
 * the selection, ✕ or the backdrop closes without changes.
 */
export function TobiIconPicker({ owner, value, onChange, labelVariant = 'caption' }: TobiIconPickerProps) {
  const [open, setOpen] = useState(false);
  const current = resolveIcon(value, owner);
  const [draft, setDraft] = useState(current.id);

  const show = () => {
    setDraft(current.id);
    setOpen(true);
  };
  const confirm = () => {
    onChange(draft);
    setOpen(false);
  };

  return (
    <View style={styles.field}>
      <Pressable
        accessibilityRole="button"
        accessibilityLabel={`Иконка: ${current.label}. Изменить`}
        onPress={show}
        style={({ pressed }) => [styles.row, pressed && styles.pressed]}
      >
        <AppText variant={labelVariant === 'heading' ? 'h3' : 'bodyStrong'} style={styles.rowLabel}>
          Иконка
        </AppText>
        <Icon name="chevron-forward-outline" color="textSecondary" size={20} />
        <TobiIcon iconId={current.id} owner={owner} size={44} />
      </Pressable>

      <Modal visible={open} transparent animationType="slide" onRequestClose={() => setOpen(false)}>
        <Pressable style={styles.backdrop} onPress={() => setOpen(false)} accessibilityLabel="Закрыть выбор иконки" />
        <View style={styles.sheet}>
          <View style={styles.sheetHeader}>
            <AppText variant="h3" align="center" style={styles.sheetTitle}>
              Выбрать иконку
            </AppText>
            <Pressable
              accessibilityRole="button"
              accessibilityLabel="Отмена"
              hitSlop={10}
              onPress={() => setOpen(false)}
              style={styles.close}
            >
              <Icon name="close-outline" color="textSecondary" size={26} />
            </Pressable>
          </View>
          <View style={styles.grid} accessibilityRole="radiogroup">
            {pickerIcons(owner).map((icon) => {
              const selected = icon.id === draft;
              return (
                <Pressable
                  key={icon.id}
                  accessibilityRole="radio"
                  accessibilityState={{ selected }}
                  accessibilityLabel={icon.label}
                  onPress={() => setDraft(icon.id)}
                  style={[styles.cell, selected && styles.cellSelected]}
                >
                  <TobiIcon iconId={icon.id} owner={owner} size={64} />
                </Pressable>
              );
            })}
          </View>
          <PrimaryButton title="Выбрать" onPress={confirm} />
        </View>
      </Modal>
    </View>
  );
}

const CELL = 80;

const styles = StyleSheet.create({
  field: { gap: spacing.xxs },
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: spacing.xs,
    backgroundColor: colors.surface,
    borderRadius: radius.lg,
    borderWidth: 1,
    borderColor: colors.border,
    paddingLeft: spacing.sm,
    paddingRight: spacing.xs,
    minHeight: 60,
  },
  rowLabel: { flex: 1 },
  pressed: { opacity: 0.85 },
  backdrop: { flex: 1, backgroundColor: colors.overlay },
  sheet: {
    backgroundColor: colors.background,
    borderTopLeftRadius: componentRadius.panel,
    borderTopRightRadius: componentRadius.panel,
    padding: spacing.md,
    paddingBottom: spacing.xl,
    gap: spacing.md,
    ...shadows.panel,
  },
  sheetHeader: { flexDirection: 'row', alignItems: 'center', justifyContent: 'center' },
  sheetTitle: { flex: 1 },
  close: { position: 'absolute', right: 0 },
  // 3 columns, as in the design reference.
  grid: { flexDirection: 'row', flexWrap: 'wrap', justifyContent: 'center', columnGap: spacing.md, rowGap: spacing.sm },
  cell: {
    width: CELL,
    height: CELL,
    alignItems: 'center',
    justifyContent: 'center',
    borderRadius: radius.lg,
    borderWidth: 2,
    borderColor: colors.background,
  },
  cellSelected: { borderColor: colors.primary, backgroundColor: colors.surface },
});
