import type { SqlExecutor } from '../db/types';
import type { PointSourceType, PointTransactionType } from '../db/schema';

export interface PointTransaction {
  id: string;
  type: PointTransactionType;
  /** Signed: positive = accrual, negative = debit. */
  amount: number;
  createdAt: string;
  calendarDate: string;
  sourceType: PointSourceType;
  sourceId: string;
  titleSnapshot: string;
}

interface Row {
  id: string;
  type: PointTransactionType;
  amount: number;
  created_at: string;
  calendar_date: string;
  source_type: PointSourceType;
  source_id: string;
  title_snapshot: string;
}

const map = (r: Row): PointTransaction => ({
  id: r.id,
  type: r.type,
  amount: r.amount,
  createdAt: r.created_at,
  calendarDate: r.calendar_date,
  sourceType: r.source_type,
  sourceId: r.source_id,
  titleSnapshot: r.title_snapshot,
});

export const pointTransactionsRepository = {
  async insert(db: SqlExecutor, t: PointTransaction): Promise<void> {
    await db.runAsync(
      `INSERT INTO point_transactions
        (id, type, amount, created_at, calendar_date, source_type, source_id, title_snapshot)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?)`,
      [t.id, t.type, t.amount, t.createdAt, t.calendarDate, t.sourceType, t.sourceId, t.titleSnapshot],
    );
  },

  async sumAll(db: SqlExecutor): Promise<number> {
    const row = await db.getFirstAsync<{ total: number | null }>('SELECT SUM(amount) AS total FROM point_transactions');
    return row?.total ?? 0;
  },

  async listAll(db: SqlExecutor): Promise<PointTransaction[]> {
    const rows = await db.getAllAsync<Row>('SELECT * FROM point_transactions ORDER BY created_at, rowid');
    return rows.map(map);
  },
};
