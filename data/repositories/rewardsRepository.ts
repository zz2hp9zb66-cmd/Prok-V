import { RewardStatus, type RewardType } from '../db/schema';
import type { SqlExecutor } from '../db/types';

export interface Reward {
  id: string;
  type: RewardType;
  name: string;
  cost: number;
  status: RewardStatus;
  createdAt: string;
  updatedAt: string;
  redeemedAt: string | null;
}

interface Row {
  id: string;
  type: RewardType;
  name: string;
  cost: number;
  status: RewardStatus;
  created_at: string;
  updated_at: string;
  redeemed_at: string | null;
}

const map = (r: Row): Reward => ({
  id: r.id,
  type: r.type,
  name: r.name,
  cost: r.cost,
  status: r.status,
  createdAt: r.created_at,
  updatedAt: r.updated_at,
  redeemedAt: r.redeemed_at,
});

export const rewardsRepository = {
  async insert(db: SqlExecutor, r: Reward): Promise<void> {
    await db.runAsync(
      `INSERT INTO rewards (id, type, name, cost, status, created_at, updated_at, redeemed_at)
       VALUES (?, ?, ?, ?, ?, ?, ?, ?)`,
      [r.id, r.type, r.name, r.cost, r.status, r.createdAt, r.updatedAt, r.redeemedAt],
    );
  },

  async update(db: SqlExecutor, r: Reward): Promise<void> {
    await db.runAsync(
      'UPDATE rewards SET name = ?, cost = ?, status = ?, updated_at = ?, redeemed_at = ? WHERE id = ?',
      [r.name, r.cost, r.status, r.updatedAt, r.redeemedAt, r.id],
    );
  },

  async delete(db: SqlExecutor, id: string): Promise<void> {
    await db.runAsync('DELETE FROM rewards WHERE id = ?', [id]);
  },

  async findById(db: SqlExecutor, id: string): Promise<Reward | null> {
    const row = await db.getFirstAsync<Row>('SELECT * FROM rewards WHERE id = ?', [id]);
    return row ? map(row) : null;
  },

  async listActiveByType(db: SqlExecutor, type: RewardType): Promise<Reward[]> {
    const rows = await db.getAllAsync<Row>(
      'SELECT * FROM rewards WHERE status = ? AND type = ? ORDER BY created_at, rowid',
      [RewardStatus.Active, type],
    );
    return rows.map(map);
  },

  async listRedeemed(db: SqlExecutor): Promise<Reward[]> {
    const rows = await db.getAllAsync<Row>(
      'SELECT * FROM rewards WHERE status = ? ORDER BY redeemed_at DESC, rowid DESC',
      [RewardStatus.Redeemed],
    );
    return rows.map(map);
  },
};
