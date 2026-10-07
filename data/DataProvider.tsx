import { SQLiteProvider, useSQLiteContext } from 'expo-sqlite';
import { createContext, type ReactNode, useContext, useMemo } from 'react';
import { type Clock, systemClock } from '@/services/time';
import { type IdGenerator, uuidGenerator } from '@/services/ids';
import { type FeedbackService, noopFeedback } from '@/services/feedback';
import { createExpoDatabase } from './db/expoDatabase';
import { migrate } from './db/migrations';
import type { SqlDatabase } from './db/types';

export const DATABASE_NAME = 'tobi-habit.db';

export interface AppServices {
  db: SqlDatabase;
  clock: Clock;
  ids: IdGenerator;
  feedback: FeedbackService;
}

const ServicesContext = createContext<AppServices | null>(null);

function ServicesBridge({ children }: { children: ReactNode }) {
  const sqlite = useSQLiteContext();
  const services = useMemo<AppServices>(
    () => ({ db: createExpoDatabase(sqlite), clock: systemClock, ids: uuidGenerator, feedback: noopFeedback }),
    [sqlite],
  );
  return <ServicesContext.Provider value={services}>{children}</ServicesContext.Provider>;
}

async function initDatabase(sqlite: Parameters<typeof createExpoDatabase>[0]) {
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

export function useServices(): AppServices {
  const services = useContext(ServicesContext);
  if (!services) throw new Error('useServices must be used inside <DataProvider>.');
  return services;
}
