import { DatabaseSync } from 'node:sqlite';
import { migrate } from '@/data/db/migrations';
import type { SqlDatabase, SqlExecutor, SqlValue } from '@/data/db/types';

/**
 * In-memory SQLite (node:sqlite) implementing the app's SqlDatabase
 * interface, so repositories and domain services run unchanged in tests.
 */
export function createTestDatabase(): SqlDatabase {
  const raw = new DatabaseSync(':memory:');
  let inTransaction = false;

  const executor: SqlExecutor = {
    execAsync: async (sql) => {
      raw.exec(sql);
    },
    runAsync: async (sql, params: readonly SqlValue[] = []) => {
      const result = raw.prepare(sql).run(...params);
      return { changes: Number(result.changes) };
    },
    getFirstAsync: async <T>(sql: string, params: readonly SqlValue[] = []) =>
      ((raw.prepare(sql).get(...params) as T | undefined) ?? null),
    getAllAsync: async <T>(sql: string, params: readonly SqlValue[] = []) => raw.prepare(sql).all(...params) as T[],
  };

  return {
    ...executor,
    transaction: async (task) => {
      if (inTransaction) return task(executor);
      inTransaction = true;
      raw.exec('BEGIN IMMEDIATE');
      try {
        const result = await task(executor);
        raw.exec('COMMIT');
        return result;
      } catch (error) {
        raw.exec('ROLLBACK');
        throw error;
      } finally {
        inTransaction = false;
      }
    },
  };
}

export async function createMigratedTestDatabase(): Promise<SqlDatabase> {
  const db = createTestDatabase();
  await migrate(db);
  return db;
}
