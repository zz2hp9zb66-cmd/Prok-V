import type { Weekday } from './time';

/** Russian-only UI (decision D6): plural forms and date formatting. */
export function pluralRu(n: number, one: string, few: string, many: string): string {
  const mod10 = Math.abs(n) % 10;
  const mod100 = Math.abs(n) % 100;
  if (mod10 === 1 && mod100 !== 11) return one;
  if (mod10 >= 2 && mod10 <= 4 && (mod100 < 12 || mod100 > 14)) return few;
  return many;
}

export function formatPoints(n: number): string {
  return `${n} ${pluralRu(n, 'балл', 'балла', 'баллов')}`;
}

export function formatDays(n: number): string {
  return `${n} ${pluralRu(n, 'день', 'дня', 'дней')}`;
}

export function formatTimes(n: number): string {
  return `${n} ${pluralRu(n, 'раз', 'раза', 'раз')}`;
}

export const WEEKDAY_SHORT: Record<Weekday, string> = { 0: 'ПН', 1: 'ВТ', 2: 'СР', 3: 'ЧТ', 4: 'ПТ', 5: 'СБ', 6: 'ВС' };
/** Title case for day toggles (Пн | Вт | …). */
export const WEEKDAY_TITLE: Record<Weekday, string> = { 0: 'Пн', 1: 'Вт', 2: 'Ср', 3: 'Чт', 4: 'Пт', 5: 'Сб', 6: 'Вс' };
export const WEEKDAY_LONG: Record<Weekday, string> = {
  0: 'Понедельник',
  1: 'Вторник',
  2: 'Среда',
  3: 'Четверг',
  4: 'Пятница',
  5: 'Суббота',
  6: 'Воскресенье',
};

export function formatWeekdays(days: readonly Weekday[]): string {
  if (days.length === 7) return 'Каждый день';
  return days.map((d) => WEEKDAY_SHORT[d]).join(', ');
}

const MONTHS_GENITIVE = [
  'января', 'февраля', 'марта', 'апреля', 'мая', 'июня',
  'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря',
];

/** «7 октября 2026» in local time. */
export function formatDate(iso: string): string {
  const d = new Date(iso);
  return `${d.getDate()} ${MONTHS_GENITIVE[d.getMonth()]} ${d.getFullYear()}`;
}

/** «09:05» in local time. */
export function formatTime(iso: string): string {
  const d = new Date(iso);
  return `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`;
}
