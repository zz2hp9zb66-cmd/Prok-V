import type { DomainContext } from '@/data/context';
import { completionsRepository } from '@/data/repositories/completionsRepository';
import { addDays, type CalendarDate, toCalendarDate, weekdayOf } from '@/services/time';

export interface WeekDayStat {
  date: CalendarDate;
  count: number;
}

export interface Statistics {
  todayCount: number;
  weekCount: number;
  weekPoints: number;
  /** Mon..Sun of the current calendar week; future days are 0 (D4). */
  weekByDay: WeekDayStat[];
  allTimeCount: number;
  allTimePoints: number;
  currentStreak: number;
}

export function startOfWeek(date: CalendarDate): CalendarDate {
  return addDays(date, -weekdayOf(date));
}

/**
 * Streak (§17, D2): consecutive calendar days with ≥1 completion. Today counts
 * if it already has a completion; an unfinished today never breaks the streak.
 * `activeDatesDesc` must be distinct dates ≤ today, newest first.
 */
export function computeStreak(activeDatesDesc: readonly CalendarDate[], today: CalendarDate): number {
  const active = new Set(activeDatesDesc);
  let day = active.has(today) ? today : addDays(today, -1);
  let streak = 0;
  while (active.has(day)) {
    streak++;
    day = addDays(day, -1);
  }
  return streak;
}

/** Computed from completion history; reversed completions are excluded. */
export async function getStatistics(ctx: DomainContext): Promise<Statistics> {
  const today = toCalendarDate(ctx.clock.now());
  const weekStart = startOfWeek(today);
  const weekEnd = addDays(weekStart, 6);

  const [weekTotals, totals, activeDates] = await Promise.all([
    completionsRepository.dailyTotals(ctx.db, weekStart, weekEnd),
    completionsRepository.totals(ctx.db),
    completionsRepository.activeDatesDesc(ctx.db, today),
  ]);

  const byDate = new Map(weekTotals.map((t) => [t.calendarDate, t]));
  const weekByDay = Array.from({ length: 7 }, (_, i) => {
    const date = addDays(weekStart, i);
    return { date, count: byDate.get(date)?.count ?? 0 };
  });

  return {
    todayCount: byDate.get(today)?.count ?? 0,
    weekCount: weekTotals.reduce((s, t) => s + t.count, 0),
    weekPoints: weekTotals.reduce((s, t) => s + t.points, 0),
    weekByDay,
    allTimeCount: totals.count,
    allTimePoints: totals.points,
    currentStreak: computeStreak(activeDates, today),
  };
}
