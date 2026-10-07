/**
 * Central time service — spec §8, §27.
 * Events store exact time (ISO, UTC). Daily logic uses the LOCAL calendar
 * date of the device; a new day starts at 00:00 local time.
 * All date math in the app must go through this module.
 */

/** Local calendar date in `YYYY-MM-DD` format. */
export type CalendarDate = string & { readonly __brand: 'CalendarDate' };

/** Weekday index: 0 = Monday … 6 = Sunday (ПН–ВС). */
export type Weekday = 0 | 1 | 2 | 3 | 4 | 5 | 6;

export const WEEKDAYS: readonly Weekday[] = [0, 1, 2, 3, 4, 5, 6];

export interface Clock {
  now(): Date;
}

export const systemClock: Clock = {
  now: () => new Date(),
};

const pad = (n: number) => String(n).padStart(2, '0');

/** Exact event timestamp for storage. */
export function toTimestamp(date: Date): string {
  return date.toISOString();
}

/** Local calendar date of a moment in time. */
export function toCalendarDate(date: Date): CalendarDate {
  return `${date.getFullYear()}-${pad(date.getMonth() + 1)}-${pad(date.getDate())}` as CalendarDate;
}

export function isCalendarDate(value: string): value is CalendarDate {
  if (!/^\d{4}-\d{2}-\d{2}$/.test(value)) return false;
  return toCalendarDate(parseCalendarDate(value as CalendarDate)) === value;
}

/** Local midnight of the given calendar date. */
export function parseCalendarDate(date: CalendarDate): Date {
  const [y, m, d] = date.split('-').map(Number) as [number, number, number];
  return new Date(y, m - 1, d);
}

export function addDays(date: CalendarDate, days: number): CalendarDate {
  const d = parseCalendarDate(date);
  d.setDate(d.getDate() + days);
  return toCalendarDate(d);
}

/** Weekday of a calendar date, Monday-based. */
export function weekdayOf(date: CalendarDate): Weekday {
  return ((parseCalendarDate(date).getDay() + 6) % 7) as Weekday;
}

export function compareCalendarDates(a: CalendarDate, b: CalendarDate): number {
  return a < b ? -1 : a > b ? 1 : 0;
}

/** Milliseconds from `now` until the next local 00:00. */
export function msUntilNextDay(now: Date): number {
  const next = new Date(now.getFullYear(), now.getMonth(), now.getDate() + 1);
  return next.getTime() - now.getTime();
}

/** Weekday set ↔ bitmask (bit 0 = Monday) used for storage. */
export function weekdaysToMask(days: readonly Weekday[]): number {
  return days.reduce<number>((mask, day) => mask | (1 << day), 0);
}

export function maskToWeekdays(mask: number): Weekday[] {
  return WEEKDAYS.filter((day) => (mask & (1 << day)) !== 0);
}

export function isWeekdayInMask(mask: number, day: Weekday): boolean {
  return (mask & (1 << day)) !== 0;
}
