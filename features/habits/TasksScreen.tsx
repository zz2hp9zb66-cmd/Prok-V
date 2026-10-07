import { router } from 'expo-router';
import type { GestureResponderEvent } from 'react-native';
import { EmptyState } from '@/components/EmptyState';
import { HabitCard } from '@/components/HabitCard';
import { Screen } from '@/components/Screen';
import { SectionHeader } from '@/components/SectionHeader';
import { TOBIHeader } from '@/components/TOBIHeader';
import { useAction } from '@/data/useAction';
import { useScreenData } from '@/data/useScreenData';
import { getBalance } from '../points/pointsService';
import { useFlyingPoints } from '../points/useFlyingPoints';
import { useTobiReaction } from '../tobi/useTobiReaction';
import { completeHabit, listHabitsForToday } from './habitsService';

/** «Задачи» (§18): TOBI, greeting, balance and today's habits. */
export function TasksScreen() {
  const { data, reload, services } = useScreenData(async (ctx) => ({
    habits: await listHabitsForToday(ctx),
    balance: await getBalance(ctx.db),
  }));
  const { busy, run } = useAction();
  const [tobiState, reactTobi] = useTobiReaction('tobi_idle');
  const flying = useFlyingPoints();

  const complete = (habitId: string, event: GestureResponderEvent) => {
    // Capture coordinates before the async call: the event is not reusable later.
    const tap = { nativeEvent: { pageX: event.nativeEvent.pageX, pageY: event.nativeEvent.pageY } } as GestureResponderEvent;
    run(async () => {
      // Business event is persisted first; visuals follow and can never undo it (§29).
      const result = await completeHabit(services, habitId);
      flying.launch(result.pointsAwarded, tap);
      services.feedback.play('habitCompleted');
      reactTobi('tobi_habit_complete', 1600);
      await reload();
    });
  };

  const openCreate = () => router.push('/habit/new');
  const balance = (data?.balance ?? 0) - flying.pendingAmount;

  return (
    <Screen overlay={flying.overlay}>
      <TOBIHeader ref={flying.targetRef} tobiState={tobiState} title="Привет!" subtitle="Что сделаем сегодня?" balance={balance} />
      <SectionHeader title="Привычки" onAdd={openCreate} addLabel="Создать привычку" />
      {data && data.habits.length === 0 ? (
        <EmptyState
          title="Пока нет привычек"
          description="Создай привычку, выполняй её и получай баллы."
          actionTitle="Создать первую привычку"
          onAction={openCreate}
        />
      ) : null}
      {data?.habits.map((view) => (
        <HabitCard
          key={view.habit.id}
          view={view}
          busy={busy}
          onPress={() => router.push({ pathname: '/habit/[id]', params: { id: view.habit.id } })}
          onComplete={(event) => complete(view.habit.id, event)}
        />
      ))}
    </Screen>
  );
}
