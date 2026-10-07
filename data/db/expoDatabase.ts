import type { SQLiteDatabase } from 'expo-sqlite';
import type { SqlDatabase, SqlExecutor, SqlValue } from './types';

function wrapExecutor(db: SQLiteDatabase): SqlExecutor {
  return {
    execAsync: (sql) => db.execAsync(sql),
    runAsync: async (sql, params = []) => {
      const result = await db.runAsync(sql, params as SqlValue[]);
      return { changes: result.changes };
    },
    getFirstAsync: (sql, params = []) => db.getFirstAsync(sql, params as SqlValue[]),
    getAllAsync: (sql, params = []) => db.getAllAsync(sql, params as SqlValue[]),
  };
}

/** Adapts expo-sqlite to the app's SqlDatabase interface. */
export function createExpoDatabase(db: SQLiteDatabase): SqlDatabase {
  return {
    ...wrapExecutor(db),
    transaction: async (task) => {
      let result: Awaited<ReturnType<typeof task>> | undefined;
      // Exclusive transaction: other queries cannot interleave with it.
      await db.withExclusiveTransactionAsync(async (txn) => {
        result = await task(wrapExecutor(txn));
      });
      return result as Awaited<ReturnType<typeof task>>;
    },
  };
}
