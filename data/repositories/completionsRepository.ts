import type { CalendarDate } from '@/services/time';
import type { SqlExecutor } from '../db/types';

export interface HabitCompletion {
  id: string;
  habitId: string;
  habitNameSnapshot: string;
  pointsAwarded: number;
  completedAt: string;
  calendarDate: CalendarDate;
  reversedAt: string | null;
}

interface Row {
  id: string;
  habit_id: string;
  habit_name_snapshot: string;
  points_awarded: number;
  completed_at: string;
  calendar_date: string;
  reversed_at: string | null;
}

const map = (r: Row): HabitCompletion => ({
  id: r.id,
  habitId: r.habit_id,
  habitNameSnapshot: r.habit_name_snapshot,
  pointsAwarded: r.points_awarded,
  completedAt: r.completed_at,
  calendarDate: r.calendar_date as CalendarDate,
  reversedAt: r.reversed_at,
});

export const completionsRepository = {
  async insert(db: SqlExecutor, c: HabitCompletion): Promise<void> {
    await db.runAsync(
      `INSERT INTO habit_completions
        (id, habit_id, habit_name_snapshot, points_awarded, completed_at, calendar_date, reversed_at)
       VALUES (?, ?, ?, ?, ?, ?, ?)`,
      [c.id, c.habitId, c.habitNameSnapshot, c.pointsAwarded, c.completedAt, c.calendarDate, c.reversedAt],
    );
  },

  async findById(db: SqlExecutor, id: string): Promise<HabitCompletion | null> {
    const row = await db.getFirstAsync<Row>('SELECT * FROM habit_completions WHERE id = ?', [id]);
    return row ? map(row) : null;
  },

  async markReversed(db: SqlExecutor, id: string, reversedAt: string): Promise<void> {
    await db.runAsync('UPDATE habit_completions SET reversed_at = ? WHERE id = ? AND reversed_at IS NULL', [
      reversedAt,
      id,
    ]);
  },

  /** Non-reversed completions of one habit on one calendar date. */
  async listActiveForHabitOnDate(db: SqlExecutor, habitId: string, date: CalendarDate): Promise<HabitCompletion[]> {
    const rows = await db.getAllAsync<Row>(
      `SELECT * FROM habit_completions
       WHERE habit_id = ? AND calendar_date = ? AND reversed_at IS NULL
       ORDER BY completed_at, rowid`,
      [habitId, date],
    );
    return rows.map(map);
  },

  /** Non-reversed completion counts per habit for a date. */
  async countActiveByHabitOnDate(db: SqlExecutor, date: CalendarDate): Promise<Map<string, number>> {
    const rows = await db.getAllAsync<{ habit_id: string; n: number }>(
      `SELECT habit_id, COUNT(*) AS n FROM habit_completions
       WHERE calendar_date = ? AND reversed_at IS NULL GROUP BY habit_id`,
      [date],
    );
    return new Map(rows.map((r) => [r.habit_id, r.n]));
  },

  /** Daily totals of non-reversed completions in [from, to]. */
  async dailyTotals(
    db: SqlExecutor,
    from: CalendarDate,
    to: CalendarDate,
  ): Promise<{ calendarDate: CalendarDate; count: number; points: number }[]> {
    const rows = await db.getAllAsync<{ calendar_date: string; n: number; points: number }>(
      `SELECT calendar_date, COUNT(*) AS n, SUM(points_awarded) AS points FROM habit_completions
       WHERE reversed_at IS NULL AND calendar_date BETWEEN ? AND ?
       GROUP BY calendar_date`,
      [from, to],
    );
    return rows.map((r) => ({ calendarDate: r.calendar_date as CalendarDate, count: r.n, points: r.points }));
  },

  async totals(db: SqlExecutor): Promise<{ count: number; points: number }> {
    const row = await db.getFirstAsync<{ n: number; points: number | null }>(
      'SELECT COUNT(*) AS n, SUM(points_awarded) AS points FROM habit_completions WHERE reversed_at IS NULL',
    );
    return { count: row?.n ?? 0, points: row?.points ?? 0 };
  },

  /** Distinct dates with at least one non-reversed completion, newest first, up to `to`. */
  async activeDatesDesc(db: SqlExecutor, to: CalendarDate): Promise<CalendarDate[]> {
    const rows = await db.getAllAsync<{ calendar_date: string }>(
      `SELECT DISTINCT calendar_date FROM habit_completions
       WHERE reversed_at IS NULL AND calendar_date <= ?
       ORDER BY calendar_date DESC`,
      [to],
    );
    return rows.map((r) => r.calendar_date as CalendarDate);
  },
};
