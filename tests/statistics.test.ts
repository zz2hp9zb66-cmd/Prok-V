import { completeHabit, createHabit, reverseCompletion } from '@/features/habits/habitsService';
import { computeStreak, getStatistics, startOfWeek } from '@/features/statistics/statisticsService';
import type { CalendarDate } from '@/services/time';
import { createTestContext } from './helpers/testContext';

const d = (s: string) => s as CalendarDate;
const everyDay = { name: 'Вода', weekdays: [0, 1, 2, 3, 4, 5, 6] as const, pointsPerCompletion: 5, dailyLimit: 5 };

describe('streak (D2)', () => {
  it('counts consecutive days including today when today is active', () => {
    expect(computeStreak([d('2026-10-07'), d('2026-10-06'), d('2026-10-05')], d('2026-10-07'))).toBe(3);
  });

  it('does not break because today is not finished yet', () => {
    expect(computeStreak([d('2026-10-06'), d('2026-10-05')], d('2026-10-07'))).toBe(2);
  });

  it('resets after a full day without completions', () => {
    expect(computeStreak([d('2026-10-05')], d('2026-10-07'))).toBe(0);
    expect(computeStreak([d('2026-10-07'), d('2026-10-05')], d('2026-10-07'))).toBe(1);
    expect(computeStreak([], d('2026-10-07'))).toBe(0);
  });
});

describe('statistics', () => {
  it('uses the Monday–Sunday calendar week', () => {
    expect(startOfWeek(d('2026-10-05'))).toBe('2026-10-05');
    expect(startOfWeek(d('2026-10-11'))).toBe('2026-10-05');
    expect(startOfWeek(d('2026-10-12'))).toBe('2026-10-12');
  });

  it('computes today, week, chart, all-time and streak from history', async () => {
    const ctx = await createTestContext(new Date(2026, 9, 2, 12)); // Friday of previous week
    const habit = await createHabit(ctx, { ...everyDay, weekdays: [...everyDay.weekdays] });
    await completeHabit(ctx, habit.id); // Fri 2 Oct (previous week)
    ctx.clock.advanceDays(1);
    await completeHabit(ctx, habit.id); // Sat 3
    ctx.clock.advanceDays(1);
    await completeHabit(ctx, habit.id); // Sun 4
    ctx.clock.advanceDays(1);
    await completeHabit(ctx, habit.id); // Mon 5
    await completeHabit(ctx, habit.id); // Mon 5
    ctx.clock.advanceDays(1);
    await completeHabit(ctx, habit.id); // Tue 6
    const cancelled = await completeHabit(ctx, habit.id); // Tue 6, cancelled
    await reverseCompletion(ctx, cancelled.completion.id);

    const stats = await getStatistics(ctx);
    expect(stats.todayCount).toBe(1);
    expect(stats.weekCount).toBe(3);
    expect(stats.weekPoints).toBe(15);
    expect(stats.weekByDay.map((x) => x.count)).toEqual([2, 1, 0, 0, 0, 0, 0]);
    expect(stats.weekByDay[0]!.date).toBe('2026-10-05');
    expect(stats.allTimeCount).toBe(6);
    expect(stats.allTimePoints).toBe(30);
    expect(stats.currentStreak).toBe(5);

    ctx.clock.advanceDays(1); // Wed, nothing yet — streak kept
    expect((await getStatistics(ctx)).currentStreak).toBe(5);
    ctx.clock.advanceDays(1); // Thu — Wed was empty, streak broken
    expect((await getStatistics(ctx)).currentStreak).toBe(0);
  });

  it('starts empty', async () => {
    const ctx = await createTestContext();
    const stats = await getStatistics(ctx);
    expect(stats).toMatchObject({ todayCount: 0, weekCount: 0, allTimeCount: 0, allTimePoints: 0, currentStreak: 0 });
    expect(stats.weekByDay).toHaveLength(7);
  });
});
