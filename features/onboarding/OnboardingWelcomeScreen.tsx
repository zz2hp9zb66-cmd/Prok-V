import { router } from 'expo-router';
import { AppText } from '@/components/AppText';
import { PrimaryButton } from '@/components/PrimaryButton';
import { Screen } from '@/components/Screen';
import { TOBIHero } from '@/components/TOBIHero';
import { useServices } from '@/data/DataProvider';
import { settingsRepository } from '@/data/repositories/settingsRepository';

/**
 * Onboarding step 1–2 (§5). Placeholder until step 9 of the dev plan:
 * goal / wish / habit creation steps are added there.
 */
export function OnboardingWelcomeScreen() {
  const { db } = useServices();

  const start = async () => {
    await settingsRepository.setOnboardingCompleted(db);
    router.replace('/tasks');
  };

  return (
    <Screen scroll={false} edges={['top', 'bottom']}>
      <TOBIHero state="tobi_wave" size={220} />
      <AppText variant="h1" align="center">
        TOBI Habit
      </AppText>
      <PrimaryButton title="Начать" onPress={start} />
    </Screen>
  );
}
