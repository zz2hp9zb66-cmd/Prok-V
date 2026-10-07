import type { Clock } from '@/services/time';
import type { IdGenerator } from '@/services/ids';
import type { SqlDatabase } from './db/types';

/** Dependencies of domain services; injected so tests can control time and ids. */
export interface DomainContext {
  db: SqlDatabase;
  clock: Clock;
  ids: IdGenerator;
}
