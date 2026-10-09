import { router } from 'expo-router';
import { useState } from 'react';
import { Image, StyleSheet, useWindowDimensions, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { AppText } from '@/components/AppText';
import { PrimaryButton } from '@/components/PrimaryButton';
import { TOBIHero } from '@/components/TOBIHero';
import { colors, componentRadius, shadows, spacing } from '@/theme';
import { tobiScenes } from '../tobi/tobiAssets';

/**
 * Onboarding welcome (§5, steps 1–2). Three layers, bottom to top:
 *  1. Room background — full screen, also behind the status bar and the home indicator.
 *  2. TOBI layer — transparent slot for the future waving TOBI (`tobi_wave`).
 *  3. Content — title, description and «Начать» inside the safe area.
 *
 * `onStart` defaults to continuing onboarding. The replay from Профиль passes
 * its own handler, so viewing the welcome again never touches any data.
 */
export function WelcomeScreen({ onStart = () => router.push('/onboarding/goal') }: { onStart?: () => void }) {
  const room = tobiScenes.welcomeRoom;
  const window = useWindowDimensions();
  // TOBI box scales with the screen (render is 2:3, `contain` keeps proportions).
  const tobiSize = Math.round(Math.min(window.height * 0.44, window.width * 0.95, 420));
  // Top of the text panel, measured on layout; TOBI never stands behind it.
  const [panelTop, setPanelTop] = useState<number | null>(null);
  // Feet on the room floor (≈69% of the screen with `cover`), but always above the panel.
  const tobiBottom = Math.min(window.height * FLOOR_LINE, panelTop ?? window.height * FLOOR_LINE);

  return (
    <View style={styles.root}>
      {/* Layer 1: background */}
      {room ? (
        <Image source={room} style={styles.background} resizeMode="cover" accessibilityIgnoresInvertColors />
      ) : null}

      {/* Layer 2: TOBI — the `tobi_wave` render, or the neutral placeholder until it is provided. */}
      <View style={[StyleSheet.absoluteFill, styles.passThrough]}>
        <View style={[styles.tobiSlot, { height: tobiBottom }]} testID="welcome-tobi-layer">
          <TOBIHero state="tobi_wave" size={tobiSize} />
        </View>
      </View>

      {/* Layer 3: content */}
      <SafeAreaView style={styles.content} edges={['top', 'bottom']}>
        <View style={styles.panel} onLayout={(e) => setPanelTop(e.nativeEvent.layout.y)}>
          <AppText variant="h1" align="center">
            Привет, я TOBI!
          </AppText>
          <AppText color="textSecondary" align="center">
            Выполняй привычки, копи баллы и обменивай их на свои цели и желания.
          </AppText>
          <PrimaryButton title="Начать" onPress={onStart} />
        </View>
      </SafeAreaView>
    </View>
  );
}

/** Share of the screen height where TOBI's box ends (floor/rug area of the room). */
const FLOOR_LINE = 0.69;

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: colors.background },
  // Explicit size so the asset's intrinsic dimensions never override the full-screen fill.
  background: { position: 'absolute', top: 0, left: 0, width: '100%', height: '100%' },
  passThrough: { pointerEvents: 'none' },
  tobiSlot: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    alignItems: 'center',
    justifyContent: 'flex-end',
  },
  content: { flex: 1, justifyContent: 'flex-end', padding: spacing.sm },
  panel: {
    gap: spacing.sm,
    padding: spacing.md,
    borderRadius: componentRadius.panel,
    backgroundColor: colors.surfaceTranslucent,
    ...shadows.panel,
  },
});

/**
 * Replay of the welcome from Профиль. Read-only: does not reset onboarding and
 * does not create or change any data; «Начать» and the back gesture return to Профиль.
 */
export function WelcomeReplayScreen() {
  return <WelcomeScreen onStart={() => (router.canGoBack() ? router.back() : router.replace('/profile'))} />;
}
