import { router, useFocusEffect } from 'expo-router';
import { setStatusBarStyle } from 'expo-status-bar';
import { useCallback, useState } from 'react';
import { Image, StyleSheet, useWindowDimensions, View } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import Svg, { Defs, LinearGradient, Rect, Stop } from 'react-native-svg';
import { AppText } from '@/components/AppText';
import { PageDots } from '@/components/PageDots';
import { PrimaryButton } from '@/components/PrimaryButton';
import { TOBIHero } from '@/components/TOBIHero';
import { colors, radius, spacing } from '@/theme';
import { tobiScenes } from '../tobi/tobiAssets';
import { computeTobiFrame } from './welcomeLayout';

const SUBTITLE = 'Я ТОБИ — твой напарник\nв больших и маленьких\nдостижениях.';

/**
 * Onboarding welcome (§5, steps 1–2), approved reference layout:
 *  - TOBI's room fills the whole screen (behind status bar and home indicator),
 *    with soft dark gradients at the top (white title) and bottom (button);
 *  - large TOBI (`tobi_wave`) in the room, sized and placed from the screen
 *    proportions (see welcomeLayout.ts);
 *  - «Привет!» + subtitle top-left, «Начать →» and step dots at the bottom.
 *
 * `onStart` defaults to continuing onboarding. The replay from Профиль passes
 * its own handler, so viewing the welcome again never touches any data.
 */
export function WelcomeScreen({ onStart = () => router.push('/onboarding/goal') }: { onStart?: () => void }) {
  const room = tobiScenes.welcomeRoom;
  const insets = useSafeAreaInsets();
  const { width, height } = useWindowDimensions();
  const [textBottom, setTextBottom] = useState<number | null>(null);
  const [buttonTop, setButtonTop] = useState<number | null>(null);

  // White status bar over the dark top of the room, only while this screen is focused.
  useFocusEffect(
    useCallback(() => {
      setStatusBarStyle('light');
      return () => setStatusBarStyle('dark');
    }, []),
  );

  const tobi = textBottom !== null && buttonTop !== null ? computeTobiFrame({ width, height, textBottom, buttonTop }) : null;
  const sideGutter = Math.min(Math.max(width * 0.12, spacing.md), spacing.xl);

  return (
    <View style={styles.root}>
      {/* Layer 1: room */}
      {room ? <Image source={room} style={styles.fill} resizeMode="cover" accessibilityIgnoresInvertColors /> : null}

      {/* Layer 2: readability gradients (top for the title, bottom for the button) */}
      <Svg width={width} height={height} style={[styles.fill, styles.passThrough]}>
        <Defs>
          <LinearGradient id="welcomeTop" x1="0" y1="0" x2="0" y2="1">
            <Stop offset="0" stopColor={colors.scrim} stopOpacity={0.55} />
            <Stop offset="1" stopColor={colors.scrim} stopOpacity={0} />
          </LinearGradient>
          <LinearGradient id="welcomeBottom" x1="0" y1="0" x2="0" y2="1">
            <Stop offset="0" stopColor={colors.scrim} stopOpacity={0} />
            <Stop offset="1" stopColor={colors.scrim} stopOpacity={0.35} />
          </LinearGradient>
        </Defs>
        <Rect x={0} y={0} width={width} height={height * 0.4} fill="url(#welcomeTop)" />
        <Rect x={0} y={height * 0.72} width={width} height={height * 0.28} fill="url(#welcomeBottom)" />
      </Svg>

      {/* Layer 3: TOBI in the room (transparent render, `contain`) */}
      {tobi ? (
        <View
          style={[styles.passThrough, { position: 'absolute', left: tobi.left, top: tobi.top }]}
          testID="welcome-tobi-layer"
        >
          <TOBIHero state="tobi_wave" width={tobi.width} height={tobi.height} />
        </View>
      ) : null}

      {/* Layer 4: content */}
      <View
        style={[
          styles.content,
          { paddingTop: insets.top + spacing.sm, paddingBottom: Math.max(insets.bottom, spacing.sm) + spacing.sm },
        ]}
      >
        <View
          style={[styles.header, { paddingHorizontal: sideGutter }]}
          onLayout={(e) => setTextBottom(e.nativeEvent.layout.y + e.nativeEvent.layout.height)}
        >
          <View style={styles.titleRow}>
            <AppText variant="display" color="textOnImage" accessibilityRole="header">
              Привет!
            </AppText>
            <View style={styles.sparkle} accessibilityElementsHidden importantForAccessibility="no-hide-descendants">
              <View style={[styles.stroke, styles.strokeUpper]} />
              <View style={[styles.stroke, styles.strokeLower]} />
            </View>
          </View>
          <AppText variant="lead" color="textOnImageSecondary">
            {SUBTITLE}
          </AppText>
        </View>

        <View style={styles.spacer} />

        <View style={styles.footer} onLayout={(e) => setButtonTop(e.nativeEvent.layout.y)}>
          <PrimaryButton title="Начать" trailingIcon="arrow-forward-outline" onPress={onStart} />
          <PageDots count={3} active={0} />
        </View>
      </View>
    </View>
  );
}

const STROKE_LENGTH = spacing.md - spacing.xxs;

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: colors.accentDark },
  // Explicit size so the asset's intrinsic dimensions never override the full-screen fill.
  fill: { position: 'absolute', top: 0, left: 0, width: '100%', height: '100%' },
  passThrough: { pointerEvents: 'none' },
  content: { flex: 1 },
  header: { gap: spacing.xs },
  titleRow: { flexDirection: 'row', alignItems: 'flex-start' },
  // Two small orange accent strokes next to the title (reference detail).
  sparkle: { width: spacing.xl, height: spacing.xl, marginLeft: spacing.xxs },
  stroke: {
    position: 'absolute',
    width: spacing.xxs + 1,
    height: STROKE_LENGTH,
    borderRadius: radius.pill,
    backgroundColor: colors.primary,
  },
  strokeUpper: { left: spacing.xs + 2, top: spacing.xxs, transform: [{ rotate: '30deg' }] },
  strokeLower: { left: spacing.sm + spacing.xs, top: spacing.sm + 2, transform: [{ rotate: '65deg' }] },
  spacer: { flex: 1 },
  footer: { paddingHorizontal: spacing.md, gap: spacing.md - spacing.xxs },
});

/**
 * Replay of the welcome from Профиль. Read-only: does not reset onboarding and
 * does not create or change any data; «Начать» and the back gesture return to Профиль.
 */
export function WelcomeReplayScreen() {
  return <WelcomeScreen onStart={() => (router.canGoBack() ? router.back() : router.replace('/profile'))} />;
}
