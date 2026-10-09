import { router } from 'expo-router';
import { PanelHeading } from '@/components/PanelHeading';
import { RoomScreen } from '@/components/RoomScreen';
import { useServices } from '@/data/ServicesContext';
import { RewardType } from '@/data/db/schema';
import { settingsRepository } from '@/data/repositories/settingsRepository';
import { useAction } from '@/data/useAction';
import { HabitCreateView } from '../habits/HabitCreateScreen';
import { createHabit } from '../habits/habitsService';
import { RewardForm } from '../rewards/RewardForm';
import { createReward } from '../rewards/rewardsService';

/**
 * Onboarding (§5): goal → wish → habit → Задачи. The welcome is shown by the
 * cold-start screen (StartupScreen) before this flow. Every creation step can
 * be skipped; `onboardingCompleted` is saved at the end.
 */

const SKIP = 'Пропустить';

function RewardStep({ type, next }: { type: RewardType; next: () => void }) {
  const services = useServices();
  const { busy, run } = useAction();
  const isGoal = type === RewardType.Goal;
  return (
    <RoomScreen
      variant="form"
      tobiState={isGoal ? 'tobi_goal_create' : 'tobi_wish_create'}
      // The first step has nothing behind it (the welcome was replaced): no back button there.
      onBack={router.canGoBack() ? () => router.back() : undefined}
      bottomSafeArea
    >
      <PanelHeading
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
    </RoomScreen>
  );
}

export function OnboardingGoalScreen() {
  return <RewardStep type={RewardType.Goal} next={() => router.push('/onboarding/wish')} />;
}

export function OnboardingWishScreen() {
  return <RewardStep type={RewardType.Wish} next={() => router.push('/onboarding/habit')} />;
}

/** Onboarding step 3 of 3 (goal → wish → habit, §5): task creation design. */
export function OnboardingHabitScreen() {
  const services = useServices();
  const { busy, run } = useAction();

  const finish = async () => {
    await settingsRepository.setOnboardingCompleted(services.db);
    router.replace('/tasks');
  };

  return (
    <HabitCreateView
      step={{ current: 3, total: 3 }}
      busy={busy}
      onBack={() => router.back()}
      onSubmit={(input) =>
        run(async () => {
          await createHabit(services, input);
          await finish();
        })
      }
      onSkip={() => run(finish)}
    />
  );
}
