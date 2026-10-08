import { router } from 'expo-router';
import { StyleSheet, View } from 'react-native';
import { AppText } from '@/components/AppText';
import { PrimaryButton } from '@/components/PrimaryButton';
import { Screen } from '@/components/Screen';
import { TOBIHero } from '@/components/TOBIHero';
import { useServices } from '@/data/ServicesContext';
import { RewardType } from '@/data/db/schema';
import { settingsRepository } from '@/data/repositories/settingsRepository';
import { useAction } from '@/data/useAction';
import { spacing } from '@/theme';
import { HabitForm } from '../habits/HabitForm';
import { createHabit } from '../habits/habitsService';
import { RewardForm } from '../rewards/RewardForm';
import { createReward } from '../rewards/rewardsService';

/**
 * Onboarding (§5): welcome → goal → wish → habit → Задачи.
 * Every creation step can be skipped; `onboardingCompleted` is saved at the end.
 */

const SKIP = 'Пропустить';

export { WelcomeScreen as OnboardingWelcomeScreen } from './WelcomeScreen';

function StepHeader({ title, text, tobi }: { title: string; text: string; tobi: Parameters<typeof TOBIHero>[0]['state'] }) {
  return (
    <View style={styles.header}>
      <TOBIHero state={tobi} size={150} />
      <AppText variant="h2" align="center">
        {title}
      </AppText>
      <AppText color="textSecondary" align="center">
        {text}
      </AppText>
    </View>
  );
}

function RewardStep({ type, next }: { type: RewardType; next: () => void }) {
  const services = useServices();
  const { busy, run } = useAction();
  const isGoal = type === RewardType.Goal;
  return (
    <Screen edges={['top', 'bottom']}>
      <StepHeader
        tobi={isGoal ? 'tobi_goal_create' : 'tobi_wish_create'}
        title={isGoal ? 'Твоя первая цель' : 'Твоё первое желание'}
        text={isGoal ? 'Что-то большое, ради чего стоит копить баллы.' : 'Небольшая радость, которую можно получить за баллы.'}
      />
      <RewardForm
        type={type}
        submitTitle="Создать"
        busy={busy}
        onSubmit={(input) =>
          run(async () => {
            await createReward(services, type, input);
            next();
          })
        }
        secondary={{ title: SKIP, onPress: next }}
      />
    </Screen>
  );
}

export function OnboardingGoalScreen() {
  return <RewardStep type={RewardType.Goal} next={() => router.push('/onboarding/wish')} />;
}

export function OnboardingWishScreen() {
  return <RewardStep type={RewardType.Wish} next={() => router.push('/onboarding/habit')} />;
}

export function OnboardingHabitScreen() {
  const services = useServices();
  const { busy, run } = useAction();

  const finish = async () => {
    await settingsRepository.setOnboardingCompleted(services.db);
    router.replace('/tasks');
  };

  return (
    <Screen edges={['top', 'bottom']}>
      <StepHeader
        tobi="tobi_habit_create"
        title="Твоя первая привычка"
        text="Выбери дни, баллы за выполнение и сколько раз в день её можно выполнить."
      />
      <HabitForm
        submitTitle="Создать"
        busy={busy}
        onSubmit={(input) =>
          run(async () => {
            await createHabit(services, input);
            await finish();
          })
        }
        secondary={{ title: SKIP, onPress: () => run(finish) }}
      />
    </Screen>
  );
}

const styles = StyleSheet.create({
  header: { gap: spacing.xs, paddingVertical: spacing.sm },
});
