import type { ReactNode } from 'react';
import { Image, type ImageSourcePropType, StyleSheet, useWindowDimensions, View } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { TOBI_ROOM_SHARED } from '@/features/tobi/tobiAssets';
import { colors, componentRadius } from '@/theme';

/**
 * `form` — creation screens (goal, wish, task): taller room, TOBI is the hero.
 * `section` — tab sections (Задачи, Награды, Статистика): shorter room so the content starts higher.
 */
export type RoomHeaderVariant = 'form' | 'section';

/** How far the cream content panel overlaps the bottom of the room. */
export const ROOM_PANEL_OVERLAP = componentRadius.panel;

const HEIGHT_RULES: Record<RoomHeaderVariant, { share: number; min: number; max: number }> = {
  form: { share: 0.26, min: 170, max: 280 },
  section: { share: 0.2, min: 140, max: 210 },
};
const GAP_UNDER_STATUS_BAR = 4;
const MAX_CHARACTER_WIDTH = 0.96;

/** Header height for a screen: a share of the screen height (clamped) plus the status bar area. */
export function roomHeaderHeight(variant: RoomHeaderVariant, screenHeight: number, insetTop: number): number {
  const r = HEIGHT_RULES[variant];
  return Math.round(Math.min(Math.max(screenHeight * r.share, r.min), r.max)) + insetTop;
}

export interface RoomCharacterInput {
  screenWidth: number;
  insetTop: number;
  headerHeight: number;
  /** Render width / height. */
  aspect: number;
  /** 1 = from under the status bar down to the panel edge. */
  scale?: number;
  /** Horizontal shift as a share of the screen width (+ = right). */
  offsetX?: number;
  /** Vertical shift as a share of the character height (+ = down, behind the panel). */
  offsetY?: number;
}

export interface RoomCharacterFrame {
  left: number;
  top: number;
  width: number;
  height: number;
}

/**
 * Character box inside the header. By default TOBI stands on the panel edge,
 * fills the height between the status bar and the panel, is centred and at
 * most 96% of the screen wide. Proportions always follow `aspect`.
 */
export function computeRoomCharacterFrame({
  screenWidth,
  insetTop,
  headerHeight,
  aspect,
  scale = 1,
  offsetX = 0,
  offsetY = 0,
}: RoomCharacterInput): RoomCharacterFrame {
  const panelTop = headerHeight - ROOM_PANEL_OVERLAP;
  let height = Math.max(0, panelTop - insetTop - GAP_UNDER_STATUS_BAR) * scale;
  let width = height * aspect;
  const maxWidth = screenWidth * MAX_CHARACTER_WIDTH;
  if (width > maxWidth) {
    width = maxWidth;
    height = width / aspect;
  }
  return {
    left: (screenWidth - width) / 2 + offsetX * screenWidth,
    top: panelTop - height + offsetY * height,
    width,
    height,
  };
}

export interface TOBIRoomHeaderProps {
  variant: RoomHeaderVariant;
  /** TOBI render with transparency. Without it only the room is shown. */
  characterSource?: ImageSourcePropType | null;
  /** Render width / height (from the registry). */
  characterAspect?: number;
  characterScale?: number;
  characterOffsetX?: number;
  characterOffsetY?: number;
  /** Extra overlay inside the header (e.g. a back button). */
  children?: ReactNode;
}

/**
 * Layer 1 — TOBI's shared room (`cover`, full width, behind the status bar).
 * Layer 2 — TOBI (`contain`, no frame, does not intercept touches).
 * The UI (layer 3) is rendered by the screen on top, starting at
 * `height - ROOM_PANEL_OVERLAP`.
 */
export function TOBIRoomHeader({
  variant,
  characterSource,
  characterAspect = 1,
  characterScale,
  characterOffsetX,
  characterOffsetY,
  children,
}: TOBIRoomHeaderProps) {
  const insets = useSafeAreaInsets();
  const { width, height: screenHeight } = useWindowDimensions();
  const height = roomHeaderHeight(variant, screenHeight, insets.top);
  const frame = characterSource
    ? computeRoomCharacterFrame({
        screenWidth: width,
        insetTop: insets.top,
        headerHeight: height,
        aspect: characterAspect,
        scale: characterScale,
        offsetX: characterOffsetX,
        offsetY: characterOffsetY,
      })
    : null;

  return (
    <View style={[styles.header, { height }]} testID="room-header">
      <Image source={TOBI_ROOM_SHARED} style={styles.room} resizeMode="cover" testID="room-background" />
      {frame && characterSource ? (
        <View style={[styles.character, { left: frame.left, top: frame.top }]} testID="room-character">
          <Image
            source={characterSource}
            style={{ width: frame.width, height: frame.height }}
            resizeMode="contain"
            accessibilityLabel="TOBI"
          />
        </View>
      ) : null}
      {children}
    </View>
  );
}

const styles = StyleSheet.create({
  header: { overflow: 'hidden', backgroundColor: colors.surfaceMuted },
  // Explicit size so the asset's intrinsic dimensions never override the fill.
  room: { position: 'absolute', top: 0, left: 0, width: '100%', height: '100%' },
  character: { position: 'absolute', pointerEvents: 'none' },
});
