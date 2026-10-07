import { router, useLocalSearchParams } from 'expo-router';
import { useState } from 'react';
import { StyleSheet, View } from 'react-native';
import { AppText } from '@/components/AppText';
import { Card } from '@/components/Card';
import { ConfirmationModal } from '@/components/ConfirmationModal';
import { EmptyState } from '@/components/EmptyState';
import { ProgressBar } from '@/components/ProgressBar';
import { Screen } from '@/components/Screen';
import { SecondaryButton } from '@/components/SecondaryButton';
import { PrimaryButton } from '@/components/PrimaryButton';
import { TOBIHero } from '@/components/TOBIHero';
import { useServices } from '@/data/ServicesContext';
import { useAction } from '@/data/useAction';
import { useScreenData } from '@/data/useScreenData';
import { formatPoints, formatTime, formatTimes, formatWeekdays } from '@/services/format';
import { spacing } from '@/theme';
import { getBalance } from '../points/pointsService';
import { HabitForm } from './HabitForm';
import { canReverse, createHabit, deleteHabit, getHabitDetails, reverseCompletion, updateHabit } from './habitsService';

const EDIT_NOTE = 'Новые баллы и лимит начнут действовать с завтрашнего дня. Название и дни недели меняются сразу.';

export function HabitCreateScreen() {
  const services = useServices();
  const { busy, run } = useAction();
  return (
    <Screen edges={['bottom']}>
      <TOBIHero state="tobi_habit_create" size={140} />
      <HabitForm
        submitTitle="Создать привычку"
        busy={busy}
        onSubmit={(input) =>
          run(async () => {
            await createHabit(services, input);
            router.back();
          })
        }
      />
    </Screen>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <View style={styles.row}>
      <AppText color="textSecondary">{label}</AppText>
      <AppText variant="bodyStrong" style={styles.value}>
        {value}
      </AppText>
    </View>
  );
}

/** Habit screen (§18): name, days, points, limit, today's state; edit / delete. */
export function HabitDetailsScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const { data, reload, today, services } = useScreenData(async (ctx) => ({
    details: await getHabitDetails(ctx, id),
    balance: await getBalance(ctx.db),
  }));
  const { busy, run } = useAction();
  const [confirmDelete, setConfirmDelete] = useState(false);

  if (!data) return null;
  const { details, balance } = data;
  if (!details) {
    return (
      <Screen edges={['bottom']}>
        <EmptyState title="Привычка не найдена" />
      </Screen>
    );
  }
  const { habit } = details;

  const todayState = !details.scheduledToday
    ? 'Сегодня не запланирована'
    : `Выполнено ${details.completedToday} из ${details.dailyLimit}`;

  return (
    <Screen edges={['bottom']}>
      <AppText variant="h1">{habit.name}</AppText>
      <Card>
        <Row label="Дни" value={formatWeekdays(habit.weekdays)} />
        <Row label="Баллы за выполнение" value={formatPoints(details.pointsPerCompletion)} />
        <Row label="Лимит в день" value={formatTimes(details.dailyLimit)} />
        {details.upcoming ? (
          <AppText variant="caption" color="info">
            С завтра: {formatPoints(details.upcoming.pointsPerCompletion)}, {formatTimes(details.upcoming.dailyLimit)} в день
          </AppText>
        ) : null}
      </Card>

      <Card muted={!details.scheduledToday}>
        <AppText variant="h3">Сегодня</AppText>
        <AppText color="textSecondary">{todayState}</AppText>
        {details.scheduledToday ? <ProgressBar progress={details.completedToday / details.dailyLimit} /> : null}
        {details.todayCompletions.map((completion) => {
          const allowed = canReverse(completion, balance, today);
          return (
            <View key={completion.id} style={styles.completion}>
              <View style={styles.completionInfo}>
                <AppText variant="bodyStrong">
                  {formatTime(completion.completedAt)} · +{formatPoints(completion.pointsAwarded)}
                </AppText>
                {!allowed ? (
                  <AppText variant="small" color="textSecondary">
                    Нельзя отменить: баллы уже потрачены
                  </AppText>
                ) : null}
              </View>
              <SecondaryButton
                title="Отменить"
                disabled={!allowed || busy}
                onPress={() =>
                  run(async () => {
                    await reverseCompletion(services, completion.id);
                    await reload();
                  })
                }
              />
            </View>
          );
        })}
      </Card>

      <PrimaryButton title="Редактировать" onPress={() => router.push({ pathname: '/habit/[id]/edit', params: { id } })} />
      <SecondaryButton title="Удалить" tone="danger" onPress={() => setConfirmDelete(true)} />

      <ConfirmationModal
        visible={confirmDelete}
        title="Удалить привычку?"
        message="Привычка исчезнет из списка. История выполнений и заработанные баллы сохранятся."
        confirmTitle="Удалить"
        destructive
        onCancel={() => setConfirmDelete(false)}
        onConfirm={() =>
          run(async () => {
            setConfirmDelete(false);
            await deleteHabit(services, id);
            router.back();
          })
        }
      />
    </Screen>
  );
}

export function HabitEditScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const { data, services } = useScreenData((ctx) => getHabitDetails(ctx, id));
  const { busy, run } = useAction();

  if (!data) return null;
  // Prefill with the latest chosen values (including ones that start tomorrow).
  const latest = data.upcoming ?? data;
  return (
    <Screen edges={['bottom']}>
      <HabitForm
        initial={{
          name: data.habit.name,
          weekdays: data.habit.weekdays,
          pointsPerCompletion: latest.pointsPerCompletion,
          dailyLimit: latest.dailyLimit,
        }}
        note={EDIT_NOTE}
        submitTitle="Сохранить"
        busy={busy}
        onSubmit={(input) =>
          run(async () => {
            await updateHabit(services, id, input);
            router.back();
          })
        }
      />
    </Screen>
  );
}

const styles = StyleSheet.create({
  row: { flexDirection: 'row', justifyContent: 'space-between', gap: spacing.sm },
  value: { flex: 1, textAlign: 'right' },
  completionInfo: { flex: 1 },
  completion: { flexDirection: 'row', alignItems: 'center', gap: spacing.sm, paddingTop: spacing.xs },
});
