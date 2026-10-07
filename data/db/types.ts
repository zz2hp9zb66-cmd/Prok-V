/**
 * Minimal async SQL interface used by repositories and domain services.
 * Implemented by expo-sqlite in the app and by node:sqlite in tests, so all
 * business logic is testable without a device.
 */
export type SqlValue = string | number | null;

export interface SqlRunResult {
  changes: number;
}

export interface SqlExecutor {
  execAsync(sql: string): Promise<void>;
  runAsync(sql: string, params?: readonly SqlValue[]): Promise<SqlRunResult>;
  getFirstAsync<T>(sql: string, params?: readonly SqlValue[]): Promise<T | null>;
  getAllAsync<T>(sql: string, params?: readonly SqlValue[]): Promise<T[]>;
}

export interface SqlDatabase extends SqlExecutor {
  /**
   * Runs `task` atomically (§26): everything is committed together or rolled
   * back on error. Nested calls join the outer transaction.
   */
  transaction<T>(task: (tx: SqlExecutor) => Promise<T>): Promise<T>;
}
