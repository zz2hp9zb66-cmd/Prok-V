import type { ReactNode } from 'react';
import { KeyboardAvoidingView, Platform, ScrollView, StyleSheet, View } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import type { TobiState } from '@/features/tobi/states';
import { tobiRenders } from '@/features/tobi/tobiAssets';
import { colors, radius, spacing } from '@/theme';
import { IconButton } from './IconButton';
import { ROOM_PANEL_OVERLAP, type RoomHeaderVariant, TOBIRoomHeader } from './TOBIRoomHeader';

export interface RoomScreenProps {
  variant: RoomHeaderVariant;
  /** TOBI state for the header; if its render is not registered yet, only the room is shown. */
  tobiState?: TobiState;
  characterScale?: number;
  characterOffsetX?: number;
  characterOffsetY?: number;
  /** Shows a round back button over the room. */
  onBack?: () => void;
  /** Fixed area under the scroll view that stays above the keyboard (e.g. «Продолжить»). */
  footer?: ReactNode;
  /** Absolutely positioned layer over the whole screen (e.g. flying points). */
  overlay?: ReactNode;
  /** Add the bottom safe area under the content (screens without a tab bar or footer). */
  bottomSafeArea?: boolean;
  children: ReactNode;
}

/**
 * Screen with TOBI's room on top and a cream panel with the UI below.
 * The panel scrolls with the room; the keyboard never covers the inputs.
 */
export function RoomScreen({
  variant,
  tobiState,
  characterScale,
  characterOffsetX,
  characterOffsetY,
  onBack,
  footer,
  overlay,
  bottomSafeArea = false,
  children,
}: RoomScreenProps) {
  const insets = useSafeAreaInsets();
  const render = tobiState ? tobiRenders[tobiState] : undefined;

  return (
    <View style={styles.root}>
      <KeyboardAvoidingView style={styles.fill} behavior={Platform.OS === 'ios' ? 'padding' : undefined}>
        <ScrollView keyboardShouldPersistTaps="handled" contentContainerStyle={styles.scroll} bounces={false}>
          <TOBIRoomHeader
            variant={variant}
            characterSource={render?.source}
            characterAspect={render ? render.width / render.height : undefined}
            characterScale={characterScale ?? render?.placement?.scale}
            characterOffsetX={characterOffsetX ?? render?.placement?.offsetX}
            characterOffsetY={characterOffsetY ?? render?.placement?.offsetY}
          />
          <View style={[styles.panel, bottomSafeArea && !footer ? { paddingBottom: spacing.md + insets.bottom } : null]}>
            {children}
          </View>
        </ScrollView>
        {footer ? (
          <View style={[styles.footer, { paddingBottom: Math.max(insets.bottom, spacing.sm) }]}>{footer}</View>
        ) : null}
      </KeyboardAvoidingView>

      {onBack ? (
        <View style={[styles.back, { top: insets.top + spacing.xs }]}>
          <IconButton icon="chevron-back-outline" tone="surface" onPress={onBack} accessibilityLabel="Назад" />
        </View>
      ) : null}
      {overlay}
    </View>
  );
}

/** Side gutter of the panel (between spacing.sm and spacing.md, as in the design). */
export const ROOM_GUTTER = spacing.sm + spacing.xxs;

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: colors.background },
  fill: { flex: 1 },
  scroll: { flexGrow: 1 },
  panel: {
    flexGrow: 1,
    marginTop: -ROOM_PANEL_OVERLAP,
    borderTopLeftRadius: radius.xl + spacing.sm,
    borderTopRightRadius: radius.xl + spacing.sm,
    backgroundColor: colors.background,
    paddingHorizontal: ROOM_GUTTER,
    paddingTop: spacing.lg,
    paddingBottom: spacing.md,
    gap: ROOM_GUTTER,
  },
  footer: {
    backgroundColor: colors.background,
    paddingHorizontal: ROOM_GUTTER,
    paddingTop: spacing.xs,
    gap: spacing.xs,
  },
  back: { position: 'absolute', left: spacing.sm },
});
