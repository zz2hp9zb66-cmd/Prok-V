import type { DomainContext } from '@/data/context';
import { PointSourceType, PointTransactionType } from '@/data/db/schema';
import type { SqlExecutor } from '@/data/db/types';
import { type HabitCompletion, completionsRepository } from '@/data/repositories/completionsRepository';
import { type HabitRecord, habitsRepository } from '@/data/repositories/habitsRepository';
import { DomainError } from '@/services/domainError';
import { addDays, type CalendarDate, toCalendarDate, toTimestamp } from '@/services/time';
import { recordPointTransaction } from '../points/pointsService';
import { effectiveParams, type HabitInput, isScheduledOn, validateHabitInput } from './habitRules';

/** Habit as seen on a given day (Tasks screen / habit screen). */
export interface HabitDayView {
  habit: HabitRecord;
  /** Points and limit in effect today. */
  pointsPerCompletion: number;
  dailyLimit: number;
  /** Values that start tomorrow, if the user changed them today. */
  upcoming: { pointsPerCompletion: number; dailyLimit: number } | null;
  scheduledToday: boolean;
  completedToday: number;
  canComplete: boolean;
}

function today(ctx: DomainContext): CalendarDate {
  return toCalendarDate(ctx.clock.now());
}

function toDayView(habit: HabitRecord, date: CalendarDate, completedToday: number): HabitDayView {
  const current = effectiveParams(habit, date);
  const hasUpcoming = habit.pendingEffectiveDate !== null && habit.pendingEffectiveDate > date;
  const scheduledToday = isScheduledOn(habit, date);
  return {
    habit,
    ...current,
    upcoming: hasUpcoming ? effectiveParams(habit, habit.pendingEffectiveDate!) : null,
    scheduledToday,
    completedToday,
    canComplete: scheduledToday && completedToday < current.dailyLimit,
  };
}

async function getActiveHabit(db: SqlExecutor, id: string): Promise<HabitRecord> {
  const habit = await habitsRepository.findById(db, id);
  if (!habit || habit.deletedAt) throw new DomainError('not_found', 'Habit not found.');
  return habit;
}

/** New habit works immediately; if today is selected it can be completed today (§11). */
export async function createHabit(ctx: DomainContext, input: HabitInput): Promise<HabitRecord> {
  const valid = validateHabitInput(input);
  const now = toTimestamp(ctx.clock.now());
  const habit: HabitRecord = {
    id: ctx.ids.next(),
    name: valid.name,
    weekdays: [...valid.weekdays],
    pointsPerCompletion: valid.pointsPerCompletion,
    dailyLimit: valid.dailyLimit,
    pendingPointsPerCompletion: null,
    pendingDailyLimit: null,
    pendingEffectiveDate: null,
    createdAt: now,
    updatedAt: now,
    deletedAt: null,
  };
  await habitsRepository.insert(ctx.db, habit);
  return habit;
}

/**
 * Name and weekdays apply immediately (D3). Points and daily limit apply from
 * the next calendar day (§11). Past completions are never recalculated.
 */
export async function updateHabit(ctx: DomainContext, id: string, input: HabitInput): Promise<HabitRecord> {
  const valid = validateHabitInput(input);
  const date = today(ctx);
  return ctx.db.transaction(async (tx) => {
    await habitsRepository.applyDuePendingChanges(tx, date);
    const habit = await getActiveHabit(tx, id);
    const pendingPoints = valid.pointsPerCompletion !== habit.pointsPerCompletion ? valid.pointsPerCompletion : null;
    const pendingLimit = valid.dailyLimit !== habit.dailyLimit ? valid.dailyLimit : null;
    const hasPending = pendingPoints !== null || pendingLimit !== null;
    const updated: HabitRecord = {
      ...habit,
      name: valid.name,
      weekdays: [...valid.weekdays],
      pendingPointsPerCompletion: pendingPoints,
      pendingDailyLimit: pendingLimit,
      pendingEffectiveDate: hasPending ? addDays(date, 1) : null,
      updatedAt: toTimestamp(ctx.clock.now()),
    };
    await habitsRepository.update(tx, updated);
    return updated;
  });
}

/** Habit disappears; completions, points and statistics stay (§11). */
export async function deleteHabit(ctx: DomainContext, id: string): Promise<void> {
  await ctx.db.transaction(async (tx) => {
    const habit = await getActiveHabit(tx, id);
    const now = toTimestamp(ctx.clock.now());
    await habitsRepository.update(tx, { ...habit, deletedAt: now, updatedAt: now });
  });
}

export async function listHabitsForToday(ctx: DomainContext): Promise<HabitDayView[]> {
  const date = today(ctx);
  const [habits, counts] = await Promise.all([
    habitsRepository.listActive(ctx.db),
    completionsRepository.countActiveByHabitOnDate(ctx.db, date),
  ]);
  return habits.map((h) => toDayView(h, date, counts.get(h.id) ?? 0));
}

export interface HabitDetails extends HabitDayView {
  /** Today's completions that can be cancelled (D1). */
  todayCompletions: HabitCompletion[];
}

export async function getHabitDetails(ctx: DomainContext, id: string): Promise<HabitDetails | null> {
  const habit = await habitsRepository.findById(ctx.db, id);
  if (!habit || habit.deletedAt) return null;
  const date = today(ctx);
  const todayCompletions = await completionsRepository.listActiveForHabitOnDate(ctx.db, id, date);
  return { ...toDayView(habit, date, todayCompletions.length), todayCompletions };
}

export interface CompletionResult {
  completion: HabitCompletion;
  pointsAwarded: number;
}

/**
 * Completes a habit (§9): completion record + point transaction in one
 * atomic step. Points are fixed at completion time.
 */
export async function completeHabit(ctx: DomainContext, habitId: string): Promise<CompletionResult> {
  const now = ctx.clock.now();
  const date = toCalendarDate(now);
  return ctx.db.transaction(async (tx) => {
    const habit = await getActiveHabit(tx, habitId);
    if (!isScheduledOn(habit, date)) {
      throw new DomainError('habit_not_scheduled_today', 'Habit is not scheduled today.');
    }
    const { pointsPerCompletion, dailyLimit } = effectiveParams(habit, date);
    const done = await completionsRepository.listActiveForHabitOnDate(tx, habitId, date);
    if (done.length >= dailyLimit) {
      throw new DomainError('habit_daily_limit_reached', 'Daily limit reached.');
    }
    const completion: HabitCompletion = {
      id: ctx.ids.next(),
      habitId,
      habitNameSnapshot: habit.name,
      pointsAwarded: pointsPerCompletion,
      completedAt: toTimestamp(now),
      calendarDate: date,
      reversedAt: null,
    };
    await completionsRepository.insert(tx, completion);
    await recordPointTransaction(tx, ctx, {
      type: PointTransactionType.HabitCompletion,
      amount: pointsPerCompletion,
      sourceType: PointSourceType.HabitCompletion,
      sourceId: completion.id,
      titleSnapshot: habit.name,
    });
    return { completion, pointsAwarded: pointsPerCompletion };
  });
}

/**
 * Cancels a completion (§10, D1): only today's completions, only if the
 * balance stays ≥ 0 after debiting the awarded points.
 */
export async function reverseCompletion(ctx: DomainContext, completionId: string): Promise<void> {
  const now = ctx.clock.now();
  const date = toCalendarDate(now);
  await ctx.db.transaction(async (tx) => {
    const completion = await completionsRepository.findById(tx, completionId);
    if (!completion) throw new DomainError('not_found', 'Completion not found.');
    if (completion.reversedAt) throw new DomainError('completion_already_reversed', 'Completion already cancelled.');
    if (completion.calendarDate !== date) {
      throw new DomainError('completion_not_today', 'Only today’s completions can be cancelled.');
    }
    // Throws insufficient_balance before anything is written if balance would go negative.
    await recordPointTransaction(tx, ctx, {
      type: PointTransactionType.HabitCompletionReversal,
      amount: -completion.pointsAwarded,
      sourceType: PointSourceType.HabitCompletion,
      sourceId: completion.id,
      titleSnapshot: completion.habitNameSnapshot,
    });
    await completionsRepository.markReversed(tx, completion.id, toTimestamp(now));
  });
}

/** Whether a completion can be cancelled right now — for disabling the UI action. */
export function canReverse(completion: HabitCompletion, balance: number, date: CalendarDate): boolean {
  return completion.reversedAt === null && completion.calendarDate === date && balance >= completion.pointsAwarded;
}
