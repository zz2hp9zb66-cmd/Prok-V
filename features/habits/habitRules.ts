import type { HabitRecord } from '@/data/repositories/habitsRepository';
import { DomainError } from '@/services/domainError';
import { type CalendarDate, WEEKDAYS, type Weekday, weekdayOf } from '@/services/time';

export interface HabitInput {
  name: string;
  weekdays: readonly Weekday[];
  pointsPerCompletion: number;
  dailyLimit: number;
}

/** Points and limit effective on `date`, taking a pending next-day change into account (§11). */
export function effectiveParams(habit: HabitRecord, date: CalendarDate): { pointsPerCompletion: number; dailyLimit: number } {
  const pendingDue = habit.pendingEffectiveDate !== null && habit.pendingEffectiveDate <= date;
  return {
    pointsPerCompletion: (pendingDue && habit.pendingPointsPerCompletion) || habit.pointsPerCompletion,
    dailyLimit: (pendingDue && habit.pendingDailyLimit) || habit.dailyLimit,
  };
}

export function isScheduledOn(habit: Pick<HabitRecord, 'weekdays'>, date: CalendarDate): boolean {
  return habit.weekdays.includes(weekdayOf(date));
}

const isPositiveInt = (n: number) => Number.isInteger(n) && n >= 1;

export function validateHabitInput(input: HabitInput): HabitInput {
  const name = input.name.trim();
  if (!name) throw new DomainError('validation', 'Habit name is required.');
  const weekdays = WEEKDAYS.filter((d) => input.weekdays.includes(d));
  if (weekdays.length === 0) throw new DomainError('validation', 'At least one weekday is required.');
  if (!isPositiveInt(input.pointsPerCompletion)) throw new DomainError('validation', 'Points must be an integer ≥ 1.');
  if (!isPositiveInt(input.dailyLimit)) throw new DomainError('validation', 'Daily limit must be an integer ≥ 1.');
  return { name, weekdays, pointsPerCompletion: input.pointsPerCompletion, dailyLimit: input.dailyLimit };
}
