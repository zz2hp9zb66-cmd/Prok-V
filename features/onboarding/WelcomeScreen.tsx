import { router } from 'expo-router';
import { Image, StyleSheet, View } from 'react-native';
import { SafeAreaView } from 'react-native-safe-area-context';
import { AppText } from '@/components/AppText';
import { PrimaryButton } from '@/components/PrimaryButton';
import { TOBIHero } from '@/components/TOBIHero';
import { colors, componentRadius, shadows, spacing } from '@/theme';
import { tobiImages, tobiScenes } from '../tobi/tobiAssets';

/**
 * Onboarding welcome (§5, steps 1–2). Three layers, bottom to top:
 *  1. Room background — full screen, also behind the status bar and the home indicator.
 *  2. TOBI layer — transparent slot for the future waving TOBI (`tobi_wave`).
 *  3. Content — title, description and «Начать» inside the safe area.
 */
export function WelcomeScreen() {
  const room = tobiScenes.welcomeRoom;
  const tobiWave = tobiImages.tobi_wave;

  return (
    <View style={styles.root}>
      {/* Layer 1: background */}
      {room ? (
        <Image source={room} style={styles.background} resizeMode="cover" accessibilityIgnoresInvertColors />
      ) : null}

      {/* Layer 2: TOBI. Over the room only a real TOBI asset is shown, never a placeholder. */}
      <SafeAreaView style={[StyleSheet.absoluteFill, styles.passThrough]} edges={['top']}>
        <View style={styles.tobiSlot} testID="welcome-tobi-layer">
          {tobiWave || !room ? <TOBIHero state="tobi_wave" size={240} /> : null}
        </View>
      </SafeAreaView>

      {/* Layer 3: content */}
      <SafeAreaView style={styles.content} edges={['top', 'bottom']}>
        <View style={styles.panel}>
          <AppText variant="h1" align="center">
            Привет, я TOBI!
          </AppText>
          <AppText color="textSecondary" align="center">
            Выполняй привычки, копи баллы и обменивай их на свои цели и желания.
          </AppText>
          <PrimaryButton title="Начать" onPress={() => router.push('/onboarding/goal')} />
        </View>
      </SafeAreaView>
    </View>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: colors.background },
  // Explicit size so the asset's intrinsic dimensions never override the full-screen fill.
  background: { position: 'absolute', top: 0, left: 0, width: '100%', height: '100%' },
  passThrough: { pointerEvents: 'none' },
  // TOBI stands on the room floor (≈62% of the image height), above the content panel.
  tobiSlot: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    height: '64%',
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
