import type { SqlExecutor } from '../db/types';

/** AppState / Settings (§25): `onboardingCompleted` and MVP settings. */
const KEYS = {
  onboardingCompleted: 'onboardingCompleted',
} as const;

async function getValue(db: SqlExecutor, key: string): Promise<string | null> {
  const row = await db.getFirstAsync<{ value: string }>('SELECT value FROM app_settings WHERE key = ?', [key]);
  return row?.value ?? null;
}

async function setValue(db: SqlExecutor, key: string, value: string): Promise<void> {
  await db.runAsync(
    'INSERT INTO app_settings (key, value) VALUES (?, ?) ON CONFLICT (key) DO UPDATE SET value = excluded.value',
    [key, value],
  );
}

export const settingsRepository = {
  async isOnboardingCompleted(db: SqlExecutor): Promise<boolean> {
    return (await getValue(db, KEYS.onboardingCompleted)) === 'true';
  },
  async setOnboardingCompleted(db: SqlExecutor): Promise<void> {
    await setValue(db, KEYS.onboardingCompleted, 'true');
  },
};
