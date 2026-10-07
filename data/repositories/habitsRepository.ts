import { type CalendarDate, maskToWeekdays, type Weekday, weekdaysToMask } from '@/services/time';
import type { SqlExecutor } from '../db/types';

/** Stored habit record (§25). Points/limit may have a pending next-day change. */
export interface HabitRecord {
  id: string;
  name: string;
  weekdays: Weekday[];
  pointsPerCompletion: number;
  dailyLimit: number;
  pendingPointsPerCompletion: number | null;
  pendingDailyLimit: number | null;
  pendingEffectiveDate: CalendarDate | null;
  createdAt: string;
  updatedAt: string;
  deletedAt: string | null;
}

interface Row {
  id: string;
  name: string;
  selected_weekdays: number;
  points_per_completion: number;
  daily_limit: number;
  pending_points_per_completion: number | null;
  pending_daily_limit: number | null;
  pending_effective_date: string | null;
  created_at: string;
  updated_at: string;
  deleted_at: string | null;
}

const map = (r: Row): HabitRecord => ({
  id: r.id,
  name: r.name,
  weekdays: maskToWeekdays(r.selected_weekdays),
  pointsPerCompletion: r.points_per_completion,
  dailyLimit: r.daily_limit,
  pendingPointsPerCompletion: r.pending_points_per_completion,
  pendingDailyLimit: r.pending_daily_limit,
  pendingEffectiveDate: r.pending_effective_date as CalendarDate | null,
  createdAt: r.created_at,
  updatedAt: r.updated_at,
  deletedAt: r.deleted_at,
});

export const habitsRepository = {
  async insert(db: SqlExecutor, h: HabitRecord): Promise<void> {
    await db.runAsync(
      `INSERT INTO habits
        (id, name, selected_weekdays, points_per_completion, daily_limit,
         pending_points_per_completion, pending_daily_limit, pending_effective_date,
         created_at, updated_at, deleted_at)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`,
      [
        h.id,
        h.name,
        weekdaysToMask(h.weekdays),
        h.pointsPerCompletion,
        h.dailyLimit,
        h.pendingPointsPerCompletion,
        h.pendingDailyLimit,
        h.pendingEffectiveDate,
        h.createdAt,
        h.updatedAt,
        h.deletedAt,
      ],
    );
  },

  async update(db: SqlExecutor, h: HabitRecord): Promise<void> {
    await db.runAsync(
      `UPDATE habits SET
         name = ?, selected_weekdays = ?, points_per_completion = ?, daily_limit = ?,
         pending_points_per_completion = ?, pending_daily_limit = ?, pending_effective_date = ?,
         updated_at = ?, deleted_at = ?
       WHERE id = ?`,
      [
        h.name,
        weekdaysToMask(h.weekdays),
        h.pointsPerCompletion,
        h.dailyLimit,
        h.pendingPointsPerCompletion,
        h.pendingDailyLimit,
        h.pendingEffectiveDate,
        h.updatedAt,
        h.deletedAt,
        h.id,
      ],
    );
  },

  /** Finds a habit, including soft-deleted ones. */
  async findById(db: SqlExecutor, id: string): Promise<HabitRecord | null> {
    const row = await db.getFirstAsync<Row>('SELECT * FROM habits WHERE id = ?', [id]);
    return row ? map(row) : null;
  },

  async listActive(db: SqlExecutor): Promise<HabitRecord[]> {
    const rows = await db.getAllAsync<Row>('SELECT * FROM habits WHERE deleted_at IS NULL ORDER BY created_at, rowid');
    return rows.map(map);
  },

  /** Moves pending points/limit that are due by `today` into the current values. */
  async applyDuePendingChanges(db: SqlExecutor, today: CalendarDate): Promise<void> {
    await db.runAsync(
      `UPDATE habits SET
         points_per_completion = COALESCE(pending_points_per_completion, points_per_completion),
         daily_limit = COALESCE(pending_daily_limit, daily_limit),
         pending_points_per_completion = NULL,
         pending_daily_limit = NULL,
         pending_effective_date = NULL
       WHERE pending_effective_date IS NOT NULL AND pending_effective_date <= ?`,
      [today],
    );
  },
};
