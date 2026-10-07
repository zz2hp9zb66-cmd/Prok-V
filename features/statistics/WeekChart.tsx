import { useState } from 'react';
import { StyleSheet, View } from 'react-native';
import Svg, { Circle, Line, Polyline } from 'react-native-svg';
import { AppText } from '@/components/AppText';
import { WEEKDAY_SHORT } from '@/services/format';
import { weekdayOf } from '@/services/time';
import { colors, spacing } from '@/theme';
import type { WeekDayStat } from './statisticsService';

const HEIGHT = 140;
const PAD = 12;

/** Line chart of completed actions per day, ПН–ВС (§18, D4). */
export function WeekChart({ days, today }: { days: WeekDayStat[]; today: string }) {
  const [width, setWidth] = useState(0);
  const max = Math.max(1, ...days.map((d) => d.count));
  const step = days.length > 1 ? (width - PAD * 2) / (days.length - 1) : 0;
  const points = days.map((d, i) => ({
    x: PAD + i * step,
    y: PAD + (HEIGHT - PAD * 2) * (1 - d.count / max),
    ...d,
  }));

  return (
    <View style={styles.container} onLayout={(e) => setWidth(e.nativeEvent.layout.width)}>
      {width > 0 ? (
        <Svg width={width} height={HEIGHT} accessibilityLabel="График выполнений за неделю">
          <Line x1={PAD} x2={width - PAD} y1={HEIGHT - PAD} y2={HEIGHT - PAD} stroke={colors.border} strokeWidth={1} />
          <Polyline
            points={points.map((p) => `${p.x},${p.y}`).join(' ')}
            fill="none"
            stroke={colors.primary}
            strokeWidth={3}
            strokeLinejoin="round"
            strokeLinecap="round"
          />
          {points.map((p) => (
            <Circle
              key={p.date}
              cx={p.x}
              cy={p.y}
              r={p.date === today ? 6 : 4}
              fill={p.date === today ? colors.primary : colors.surface}
              stroke={colors.primary}
              strokeWidth={2}
            />
          ))}
        </Svg>
      ) : (
        <View style={{ height: HEIGHT }} />
      )}
      <View style={styles.labels}>
        {days.map((d) => (
          <View key={d.date} style={styles.label}>
            <AppText variant="small" color={d.date === today ? 'primary' : 'textSecondary'}>
              {WEEKDAY_SHORT[weekdayOf(d.date)]}
            </AppText>
            <AppText variant="small" color="textPrimary">
              {d.count}
            </AppText>
          </View>
        ))}
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { gap: spacing.xxs },
  labels: { flexDirection: 'row', justifyContent: 'space-between' },
  // Width 2*PAD centers each label under its point (first at PAD, last at width - PAD).
  label: { alignItems: 'center', width: PAD * 2, overflow: 'visible' },
});
