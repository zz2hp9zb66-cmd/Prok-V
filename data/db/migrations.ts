import type { SqlDatabase } from './types';

/**
 * Ordered schema migrations. The index + 1 is the schema version stored in
 * `PRAGMA user_version`. Never edit a released migration — append a new one.
 */
export const migrations: readonly string[] = [
  // v1 — initial MVP schema (§25).
  `
  CREATE TABLE app_settings (
    key   TEXT PRIMARY KEY NOT NULL,
    value TEXT NOT NULL
  );

  CREATE TABLE habits (
    id                            TEXT PRIMARY KEY NOT NULL,
    name                          TEXT NOT NULL,
    -- Bitmask of scheduled weekdays, bit 0 = Monday … bit 6 = Sunday.
    selected_weekdays             INTEGER NOT NULL CHECK (selected_weekdays BETWEEN 0 AND 127),
    points_per_completion         INTEGER NOT NULL CHECK (points_per_completion >= 1),
    daily_limit                   INTEGER NOT NULL CHECK (daily_limit >= 1),
    -- Points / limit changes take effect from the next calendar day (§11).
    pending_points_per_completion INTEGER CHECK (pending_points_per_completion >= 1),
    pending_daily_limit           INTEGER CHECK (pending_daily_limit >= 1),
    pending_effective_date        TEXT,
    created_at                    TEXT NOT NULL,
    updated_at                    TEXT NOT NULL,
    -- Deleted habits disappear from the UI; their history stays (§11).
    deleted_at                    TEXT
  );

  CREATE TABLE habit_completions (
    id                  TEXT PRIMARY KEY NOT NULL,
    habit_id            TEXT NOT NULL REFERENCES habits (id),
    habit_name_snapshot TEXT NOT NULL,
    points_awarded      INTEGER NOT NULL CHECK (points_awarded >= 1),
    completed_at        TEXT NOT NULL,
    calendar_date       TEXT NOT NULL,
    reversed_at         TEXT
  );
  CREATE INDEX idx_habit_completions_habit_date ON habit_completions (habit_id, calendar_date);
  CREATE INDEX idx_habit_completions_date ON habit_completions (calendar_date);

  CREATE TABLE rewards (
    id          TEXT PRIMARY KEY NOT NULL,
    type        TEXT NOT NULL CHECK (type IN ('goal', 'wish')),
    name        TEXT NOT NULL,
    cost        INTEGER NOT NULL CHECK (cost >= 1),
    status      TEXT NOT NULL CHECK (status IN ('active', 'redeemed')),
    created_at  TEXT NOT NULL,
    updated_at  TEXT NOT NULL,
    redeemed_at TEXT
  );
  CREATE INDEX idx_rewards_status_type ON rewards (status, type);

  -- Single source of truth for the balance (§26). Amount is signed.
  CREATE TABLE point_transactions (
    id             TEXT PRIMARY KEY NOT NULL,
    type           TEXT NOT NULL CHECK (type IN ('habit_completion', 'habit_completion_reversal', 'reward_redemption')),
    amount         INTEGER NOT NULL CHECK (amount <> 0),
    created_at     TEXT NOT NULL,
    calendar_date  TEXT NOT NULL,
    source_type    TEXT NOT NULL CHECK (source_type IN ('habit_completion', 'reward')),
    source_id      TEXT NOT NULL,
    title_snapshot TEXT NOT NULL
  );
  CREATE INDEX idx_point_transactions_date ON point_transactions (calendar_date);
  CREATE INDEX idx_point_transactions_source ON point_transactions (source_type, source_id);
  `,
];

export const LATEST_SCHEMA_VERSION = migrations.length;

export async function getSchemaVersion(db: SqlDatabase): Promise<number> {
  const row = await db.getFirstAsync<{ user_version: number }>('PRAGMA user_version');
  return row?.user_version ?? 0;
}

/** Applies pending migrations; each one atomically together with its version bump. */
export async function migrate(db: SqlDatabase): Promise<void> {
  await db.execAsync('PRAGMA foreign_keys = ON');
  const current = await getSchemaVersion(db);
  if (current > LATEST_SCHEMA_VERSION) {
    throw new Error(`Database schema v${current} is newer than the app (v${LATEST_SCHEMA_VERSION}).`);
  }
  for (let version = current + 1; version <= LATEST_SCHEMA_VERSION; version++) {
    const sql = migrations[version - 1]!;
    await db.transaction(async (tx) => {
      await tx.execAsync(sql);
      await tx.execAsync(`PRAGMA user_version = ${version}`);
    });
  }
}
