import { AppText } from '@/components/AppText';
import { Screen } from '@/components/Screen';
import { TOBIHero } from '@/components/TOBIHero';

/** Placeholder — implemented in a later MVP step (spec §34). */
export function StatisticsScreen() {
  return (
    <Screen>
      <TOBIHero state="tobi_statistics" />
      <AppText variant="h1">Статистика</AppText>
    </Screen>
  );
}
