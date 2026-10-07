import { StyleSheet, View } from 'react-native';
import { AppText } from '@/components/AppText';
import { Card } from '@/components/Card';
import { Screen } from '@/components/Screen';
import { StatisticCard } from '@/components/StatisticCard';
import { StreakBadge } from '@/components/StreakBadge';
import { TOBIHero } from '@/components/TOBIHero';
import { useScreenData } from '@/data/useScreenData';
import { spacing } from '@/theme';
import { getStatistics } from './statisticsService';
import { WeekChart } from './WeekChart';

/** «Статистика» (§17–18): TOBI on top, weekly line chart, key numbers, streak. */
export function StatisticsScreen() {
  const { data: stats, today } = useScreenData(getStatistics);

  return (
    <Screen>
      <TOBIHero state="tobi_statistics" size={140} />
      <AppText variant="h1">Статистика</AppText>
      {stats ? (
        <>
          <StreakBadge days={stats.currentStreak} />
          <Card>
            <AppText variant="h3">Эта неделя</AppText>
            <WeekChart days={stats.weekByDay} today={today} />
          </Card>
          <View style={styles.grid}>
            <StatisticCard label="Выполнено сегодня" value={stats.todayCount} />
            <StatisticCard label="Выполнено за неделю" value={stats.weekCount} />
            <StatisticCard label="Баллов за неделю" value={stats.weekPoints} />
            <StatisticCard label="Выполнено за всё время" value={stats.allTimeCount} />
            <StatisticCard label="Баллов за всё время" value={stats.allTimePoints} />
          </View>
        </>
      ) : null}
    </Screen>
  );
}

const styles = StyleSheet.create({
  grid: { flexDirection: 'row', flexWrap: 'wrap', gap: spacing.sm },
});
