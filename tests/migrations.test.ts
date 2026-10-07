import { getSchemaVersion, LATEST_SCHEMA_VERSION, migrate } from '@/data/db/migrations';
import { settingsRepository } from '@/data/repositories/settingsRepository';
import { createMigratedTestDatabase, createTestDatabase } from './helpers/testDatabase';

describe('migrations', () => {
  it('migrates an empty database to the latest version', async () => {
    const db = createTestDatabase();
    expect(await getSchemaVersion(db)).toBe(0);
    await migrate(db);
    expect(await getSchemaVersion(db)).toBe(LATEST_SCHEMA_VERSION);

    const tables = await db.getAllAsync<{ name: string }>(
      "SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name",
    );
    expect(tables.map((t) => t.name)).toEqual([
      'app_settings',
      'habit_completions',
      'habits',
      'point_transactions',
      'rewards',
    ]);
  });

  it('is idempotent', async () => {
    const db = await createMigratedTestDatabase();
    await migrate(db);
    expect(await getSchemaVersion(db)).toBe(LATEST_SCHEMA_VERSION);
  });

  it('enforces minimum points, cost and daily limit at the schema level', async () => {
    const db = await createMigratedTestDatabase();
    const now = new Date().toISOString();
    await expect(
      db.runAsync(
        'INSERT INTO habits (id, name, selected_weekdays, points_per_completion, daily_limit, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)',
        ['h1', 'Read', 1, 0, 1, now, now],
      ),
    ).rejects.toThrow();
    await expect(
      db.runAsync(
        'INSERT INTO habits (id, name, selected_weekdays, points_per_completion, daily_limit, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)',
        ['h1', 'Read', 1, 1, 0, now, now],
      ),
    ).rejects.toThrow();
    await expect(
      db.runAsync(
        "INSERT INTO rewards (id, type, name, cost, status, created_at, updated_at) VALUES ('r1', 'goal', 'Trip', 0, 'active', ?, ?)",
        [now, now],
      ),
    ).rejects.toThrow();
  });

  it('rolls back a failed transaction completely', async () => {
    const db = await createMigratedTestDatabase();
    await expect(
      db.transaction(async (tx) => {
        await tx.runAsync("INSERT INTO app_settings (key, value) VALUES ('a', '1')");
        throw new Error('boom');
      }),
    ).rejects.toThrow('boom');
    expect(await db.getAllAsync('SELECT * FROM app_settings')).toEqual([]);
  });
});

describe('settingsRepository', () => {
  it('stores onboardingCompleted', async () => {
    const db = await createMigratedTestDatabase();
    expect(await settingsRepository.isOnboardingCompleted(db)).toBe(false);
    await settingsRepository.setOnboardingCompleted(db);
    expect(await settingsRepository.isOnboardingCompleted(db)).toBe(true);
  });
});
