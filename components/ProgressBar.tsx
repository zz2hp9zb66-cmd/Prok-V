import { StyleSheet, View } from 'react-native';
import { colors, type ColorToken, radius } from '@/theme';

export interface ProgressBarProps {
  /** 0..1 */
  progress: number;
  color?: ColorToken;
  height?: number;
}

export function ProgressBar({ progress, color = 'primary', height = 8 }: ProgressBarProps) {
  const clamped = Math.max(0, Math.min(1, progress));
  return (
    <View
      style={[styles.track, { height }]}
      accessibilityRole="progressbar"
      accessibilityValue={{ min: 0, max: 100, now: Math.round(clamped * 100) }}
    >
      <View style={[styles.fill, { width: `${clamped * 100}%`, backgroundColor: colors[color] }]} />
    </View>
  );
}

const styles = StyleSheet.create({
  track: { backgroundColor: colors.border, borderRadius: radius.pill, overflow: 'hidden' },
  fill: { height: '100%', borderRadius: radius.pill },
});
