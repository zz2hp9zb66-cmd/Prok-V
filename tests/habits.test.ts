import { completionsRepository } from '@/data/repositories/completionsRepository';
import { pointTransactionsRepository } from '@/data/repositories/pointTransactionsRepository';
import type { HabitInput } from '@/features/habits/habitRules';
import {
  completeHabit,
  createHabit,
  deleteHabit,
  getHabitDetails,
  listHabitsForToday,
  reverseCompletion,
  updateHabit,
} from '@/features/habits/habitsService';
import { getBalance } from '@/features/points/pointsService';
import { createReward, redeemReward } from '@/features/rewards/rewardsService';
import { getStatistics } from '@/features/statistics/statisticsService';
import { isDomainError } from '@/services/domainError';
import type { Weekday } from '@/services/time';
import { createTestContext } from './helpers/testContext';

const ALL_DAYS: Weekday[] = [0, 1, 2, 3, 4, 5, 6];
const habitInput = (over: Partial<HabitInput> = {}): HabitInput => ({
  name: 'Читать',
  weekdays: ALL_DAYS,
  pointsPerCompletion: 10,
  dailyLimit: 1,
  ...over,
});

const errorCode = (p: Promise<unknown>) => p.then(() => null, (e) => (isDomainError(e) ? e.code : e));

describe('habit CRUD', () => {
  it('creates a habit that is available today when today is selected', async () => {
    const ctx = await createTestContext(); // Monday
    const habit = await createHabit(ctx, habitInput({ name: '  Читать  ', weekdays: [0] }));
    expect(habit.name).toBe('Читать');
    const [view] = await listHabitsForToday(ctx);
    expect(view).toMatchObject({ scheduledToday: true, canComplete: true, completedToday: 0 });
  });

  it('validates input', async () => {
    const ctx = await createTestContext();
    expect(await errorCode(createHabit(ctx, habitInput({ name: '  ' })))).toBe('validation');
    expect(await errorCode(createHabit(ctx, habitInput({ weekdays: [] })))).toBe('validation');
    expect(await errorCode(createHabit(ctx, habitInput({ pointsPerCompletion: 0 })))).toBe('validation');
    expect(await errorCode(createHabit(ctx, habitInput({ dailyLimit: 0 })))).toBe('validation');
    expect(await errorCode(createHabit(ctx, habitInput({ dailyLimit: 2.5 })))).toBe('validation');
  });

  it('allows any large points and limit (no maximum)', async () => {
    const ctx = await createTestContext();
    const habit = await createHabit(ctx, habitInput({ pointsPerCompletion: 1_000_000, dailyLimit: 500 }));
    expect(habit).toMatchObject({ pointsPerCompletion: 1_000_000, dailyLimit: 500 });
  });

  it('deletes a habit but keeps history, points and statistics', async () => {
    const ctx = await createTestContext();
    const habit = await createHabit(ctx, habitInput());
    const { completion } = await completeHabit(ctx, habit.id);
    await deleteHabit(ctx, habit.id);

    expect(await listHabitsForToday(ctx)).toEqual([]);
    expect(await getHabitDetails(ctx, habit.id)).toBeNull();
    expect(await completionsRepository.findById(ctx.db, completion.id)).toMatchObject({ habitNameSnapshot: 'Читать' });
    expect(await getBalance(ctx.db)).toBe(10);
    expect((await getStatistics(ctx)).allTimeCount).toBe(1);
    expect(await errorCode(completeHabit(ctx, habit.id))).toBe('not_found');
  });
});

describe('schedule', () => {
  it('keeps unscheduled habits visible but inactive', async () => {
    const ctx = await createTestContext(); // Monday
    const habit = await createHabit(ctx, habitInput({ weekdays: [1, 2] }));
    const [view] = await listHabitsForToday(ctx);
    expect(view).toMatchObject({ scheduledToday: false, canComplete: false });
    expect(await errorCode(completeHabit(ctx, habit.id))).toBe('habit_not_scheduled_today');
    expect(await getBalance(ctx.db)).toBe(0);
  });

  it('follows the weekday when the day changes', async () => {
    const ctx = await createTestContext(); // Monday
    await createHabit(ctx, habitInput({ weekdays: [1] }));
    expect((await listHabitsForToday(ctx))[0]!.scheduledToday).toBe(false);
    ctx.clock.advanceDays(1); // Tuesday
    expect((await listHabitsForToday(ctx))[0]!.scheduledToday).toBe(true);
  });

  it('applies weekday changes immediately (D3)', async () => {
    const ctx = await createTestContext(); // Monday
    const habit = await createHabit(ctx, habitInput({ weekdays: [1] }));
    await updateHabit(ctx, habit.id, habitInput({ weekdays: [0, 1] }));
    expect((await listHabitsForToday(ctx))[0]!.canComplete).toBe(true);
    await completeHabit(ctx, habit.id);

    await updateHabit(ctx, habit.id, habitInput({ weekdays: [1] }));
    const [view] = await listHabitsForToday(ctx);
    expect(view).toMatchObject({ scheduledToday: false, canComplete: false });
    // History is unchanged.
    expect((await getStatistics(ctx)).todayCount).toBe(1);
    expect(await getBalance(ctx.db)).toBe(10);
  });
});

describe('daily limit and completions', () => {
  it('allows multiple completions up to the limit, then becomes inactive', async () => {
    const ctx = await createTestContext();
    const habit = await createHabit(ctx, habitInput({ dailyLimit: 3, pointsPerCompletion: 5 }));
    for (let i = 0; i < 3; i++) await completeHabit(ctx, habit.id);

    const [view] = await listHabitsForToday(ctx);
    expect(view).toMatchObject({ completedToday: 3, dailyLimit: 3, canComplete: false });
    expect(await errorCode(completeHabit(ctx, habit.id))).toBe('habit_daily_limit_reached');
    expect(await getBalance(ctx.db)).toBe(15);
  });

  it('creates completion and transaction with the points fixed at completion time', async () => {
    const ctx = await createTestContext();
    const habit = await createHabit(ctx, habitInput({ pointsPerCompletion: 7 }));
    const { completion, pointsAwarded } = await completeHabit(ctx, habit.id);
    expect(pointsAwarded).toBe(7);
    expect(completion).toMatchObject({ habitId: habit.id, calendarDate: '2026-10-05', pointsAwarded: 7 });
    const txs = await pointTransactionsRepository.listAll(ctx.db);
    expect(txs).toEqual([
      expect.objectContaining({ type: 'habit_completion', amount: 7, sourceId: completion.id }),
    ]);
  });

  it('resets daily counters at local midnight, not 24h after completion', async () => {
    const ctx = await createTestContext(new Date(2026, 9, 5, 23, 50));
    const habit = await createHabit(ctx, habitInput());
    await completeHabit(ctx, habit.id);
    expect((await listHabitsForToday(ctx))[0]!.canComplete).toBe(false);

    ctx.clock.set(new Date(2026, 9, 6, 0, 1)); // 11 minutes later, new day
    const [view] = await listHabitsForToday(ctx);
    expect(view).toMatchObject({ completedToday: 0, canComplete: true });
    await completeHabit(ctx, habit.id);
    expect(await getBalance(ctx.db)).toBe(20);
  });
});

describe('editing points and limit', () => {
  it('applies new points and limit from the next calendar day, without recalculating history', async () => {
    const ctx = await createTestContext();
    const habit = await createHabit(ctx, habitInput({ pointsPerCompletion: 10, dailyLimit: 1 }));
    await completeHabit(ctx, habit.id);

    await updateHabit(ctx, habit.id, habitInput({ name: 'Читать книгу', pointsPerCompletion: 20, dailyLimit: 2 }));
    let [view] = await listHabitsForToday(ctx);
    expect(view).toMatchObject({
      pointsPerCompletion: 10,
      dailyLimit: 1,
      canComplete: false,
      upcoming: { pointsPerCompletion: 20, dailyLimit: 2 },
    });
    expect(view!.habit.name).toBe('Читать книгу'); // name applies immediately

    ctx.clock.advanceDays(1);
    [view] = await listHabitsForToday(ctx);
    expect(view).toMatchObject({ pointsPerCompletion: 20, dailyLimit: 2, upcoming: null });
    await completeHabit(ctx, habit.id);
    await completeHabit(ctx, habit.id);

    expect(await getBalance(ctx.db)).toBe(10 + 20 + 20);
    const stats = await getStatistics(ctx);
    expect(stats.allTimePoints).toBe(50);
  });

  it('cancels a pending change when the value is set back the same day', async () => {
    const ctx = await createTestContext();
    const habit = await createHabit(ctx, habitInput({ pointsPerCompletion: 10 }));
    await updateHabit(ctx, habit.id, habitInput({ pointsPerCompletion: 20 }));
    const updated = await updateHabit(ctx, habit.id, habitInput({ pointsPerCompletion: 10 }));
    expect(updated.pendingEffectiveDate).toBeNull();
  });

  it('keeps today’s parameters when a pending change from yesterday is followed by a new edit', async () => {
    const ctx = await createTestContext();
    const habit = await createHabit(ctx, habitInput({ pointsPerCompletion: 10 }));
    await updateHabit(ctx, habit.id, habitInput({ pointsPerCompletion: 20 }));
    ctx.clock.advanceDays(1);
    await updateHabit(ctx, habit.id, habitInput({ pointsPerCompletion: 30 }));
    const [view] = await listHabitsForToday(ctx);
    expect(view).toMatchObject({ pointsPerCompletion: 20, upcoming: { pointsPerCompletion: 30 } });
    const { pointsAwarded } = await completeHabit(ctx, habit.id);
    expect(pointsAwarded).toBe(20);
  });
});

describe('cancelling a completion', () => {
  it('cancels any of today’s completions and debits its points', async () => {
    const ctx = await createTestContext();
    const habit = await createHabit(ctx, habitInput({ dailyLimit: 3 }));
    const first = await completeHabit(ctx, habit.id);
    await completeHabit(ctx, habit.id);

    await reverseCompletion(ctx, first.completion.id); // not the last one (D1)
    expect(await getBalance(ctx.db)).toBe(10);
    const details = await getHabitDetails(ctx, habit.id);
    expect(details!.completedToday).toBe(1);
    expect((await getStatistics(ctx)).todayCount).toBe(1);

    const txs = await pointTransactionsRepository.listAll(ctx.db);
    expect(txs.at(-1)).toMatchObject({ type: 'habit_completion_reversal', amount: -10, sourceId: first.completion.id });
    expect(await errorCode(reverseCompletion(ctx, first.completion.id))).toBe('completion_already_reversed');
  });

  it('frees a slot of the daily limit', async () => {
    const ctx = await createTestContext();
    const habit = await createHabit(ctx, habitInput({ dailyLimit: 1 }));
    const { completion } = await completeHabit(ctx, habit.id);
    await reverseCompletion(ctx, completion.id);
    expect((await listHabitsForToday(ctx))[0]!.canComplete).toBe(true);
  });

  it('cannot cancel completions from previous days', async () => {
    const ctx = await createTestContext();
    const habit = await createHabit(ctx, habitInput());
    const { completion } = await completeHabit(ctx, habit.id);
    ctx.clock.advanceDays(1);
    expect(await errorCode(reverseCompletion(ctx, completion.id))).toBe('completion_not_today');
    expect(await getBalance(ctx.db)).toBe(10);
  });

  it('cannot cancel after the points were spent (§10 example)', async () => {
    const ctx = await createTestContext();
    const habit = await createHabit(ctx, habitInput({ pointsPerCompletion: 100 }));
    const { completion } = await completeHabit(ctx, habit.id);
    const reward = await createReward(ctx, 'goal', { name: 'Кино', cost: 100 });
    await redeemReward(ctx, reward.id);
    expect(await getBalance(ctx.db)).toBe(0);

    expect(await errorCode(reverseCompletion(ctx, completion.id))).toBe('insufficient_balance');
    // Nothing changed: completion still active, balance still 0, no extra transaction.
    expect((await completionsRepository.findById(ctx.db, completion.id))!.reversedAt).toBeNull();
    expect(await getBalance(ctx.db)).toBe(0);
    expect(await pointTransactionsRepository.listAll(ctx.db)).toHaveLength(2);
  });
});

describe('atomicity', () => {
  it('rolls back the completion when the point transaction fails', async () => {
    const ctx = await createTestContext();
    const habit = await createHabit(ctx, habitInput());
    // Make the second id collide with an existing transaction id to force a failure mid-operation.
    let n = 0;
    const ids = ['c-1', 't-1', 'c-2', 't-1'];
    const failing = { ...ctx, ids: { next: () => ids[n++]! } };
    await completeHabit(failing, habit.id);
    await expect(completeHabit(failing, habit.id)).rejects.toThrow();

    expect(await completionsRepository.findById(ctx.db, 'c-2')).toBeNull();
    expect(await getBalance(ctx.db)).toBe(10);
  });
});
