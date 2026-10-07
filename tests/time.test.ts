import {
  addDays,
  type CalendarDate,
  isCalendarDate,
  maskToWeekdays,
  msUntilNextDay,
  toCalendarDate,
  weekdayOf,
  weekdaysToMask,
} from '@/services/time/calendar';

const d = (s: string) => s as CalendarDate;

describe('time service', () => {
  it('uses the local calendar date, switching at 00:00', () => {
    expect(toCalendarDate(new Date(2026, 9, 7, 23, 59, 59))).toBe('2026-10-07');
    expect(toCalendarDate(new Date(2026, 9, 8, 0, 0, 0))).toBe('2026-10-08');
  });

  it('computes Monday-based weekdays', () => {
    expect(weekdayOf(d('2026-10-05'))).toBe(0); // Monday
    expect(weekdayOf(d('2026-10-11'))).toBe(6); // Sunday
  });

  it('adds days across month and year boundaries', () => {
    expect(addDays(d('2026-10-31'), 1)).toBe('2026-11-01');
    expect(addDays(d('2026-12-31'), 1)).toBe('2027-01-01');
    expect(addDays(d('2026-03-01'), -1)).toBe('2026-02-28');
  });

  it('counts time until the next local midnight', () => {
    expect(msUntilNextDay(new Date(2026, 9, 7, 23, 59, 0))).toBe(60_000);
  });

  it('round-trips weekday bitmasks', () => {
    expect(weekdaysToMask([0, 2, 6])).toBe(0b1000101);
    expect(maskToWeekdays(0b1000101)).toEqual([0, 2, 6]);
  });

  it('validates calendar dates', () => {
    expect(isCalendarDate('2026-02-28')).toBe(true);
    expect(isCalendarDate('2026-02-30')).toBe(false);
    expect(isCalendarDate('2026-2-3')).toBe(false);
  });
});
