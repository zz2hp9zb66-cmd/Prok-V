import type { DomainContext } from '@/data/context';
import type { Clock } from '@/services/time';
import { createMigratedTestDatabase } from './testDatabase';

export class FakeClock implements Clock {
  constructor(private current: Date) {}
  now(): Date {
    return new Date(this.current);
  }
  set(date: Date): void {
    this.current = new Date(date);
  }
  advanceDays(days: number): void {
    const d = new Date(this.current);
    d.setDate(d.getDate() + days);
    this.current = d;
  }
}

/** Monday, 5 Oct 2026, 10:00 local time. */
export const MONDAY = () => new Date(2026, 9, 5, 10, 0, 0);

export async function createTestContext(start: Date = MONDAY()): Promise<DomainContext & { clock: FakeClock }> {
  let n = 0;
  return {
    db: await createMigratedTestDatabase(),
    clock: new FakeClock(start),
    ids: { next: () => `id-${++n}` },
  };
}
