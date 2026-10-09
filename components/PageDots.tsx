import { StyleSheet, View } from 'react-native';
import { colors, radius, spacing } from '@/theme';

/** Small page indicator dots for full-screen scenes (decorative). */
export function PageDots({ count, active }: { count: number; active: number }) {
  return (
    <View style={styles.row} accessibilityElementsHidden importantForAccessibility="no-hide-descendants">
      {Array.from({ length: count }, (_, i) => (
        <View key={i} style={[styles.dot, { backgroundColor: i === active ? colors.textOnImage : colors.textOnImageMuted }]} />
      ))}
    </View>
  );
}

const DOT = spacing.xs + 2;

const styles = StyleSheet.create({
  row: { flexDirection: 'row', justifyContent: 'center', gap: spacing.sm - spacing.xxs },
  dot: { width: DOT, height: DOT, borderRadius: radius.pill },
});
