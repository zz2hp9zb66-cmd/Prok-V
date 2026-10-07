import { type SQLiteDatabase, SQLiteProvider, useSQLiteContext } from 'expo-sqlite';
import { type ReactNode, useMemo } from 'react';
import { noopFeedback } from '@/services/feedback';
import { uuidGenerator } from '@/services/ids';
import { systemClock } from '@/services/time';
import { createExpoDatabase } from './db/expoDatabase';
import { migrate } from './db/migrations';
import { type AppServices, ServicesProvider } from './ServicesContext';

export { useServices, type AppServices } from './ServicesContext';

export const DATABASE_NAME = 'tobi-habit.db';

function ServicesBridge({ children }: { children: ReactNode }) {
  const sqlite = useSQLiteContext();
  const services = useMemo<AppServices>(
    () => ({ db: createExpoDatabase(sqlite), clock: systemClock, ids: uuidGenerator, feedback: noopFeedback }),
    [sqlite],
  );
  return <ServicesProvider value={services}>{children}</ServicesProvider>;
}

async function initDatabase(sqlite: SQLiteDatabase) {
  await sqlite.execAsync('PRAGMA journal_mode = WAL');
  await migrate(createExpoDatabase(sqlite));
}

/** Opens the local SQLite database, runs migrations and exposes app services. */
export function DataProvider({ children }: { children: ReactNode }) {
  return (
    <SQLiteProvider databaseName={DATABASE_NAME} onInit={initDatabase}>
      <ServicesBridge>{children}</ServicesBridge>
    </SQLiteProvider>
  );
}
