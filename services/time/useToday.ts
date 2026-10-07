import { useEffect, useState } from 'react';
import { AppState } from 'react-native';
import { type CalendarDate, type Clock, msUntilNextDay, systemClock, toCalendarDate } from './calendar';

/**
 * Current local calendar date that updates at 00:00 and when the app returns
 * to the foreground (handles close/reopen and crossing midnight in background).
 */
export function useToday(clock: Clock = systemClock): CalendarDate {
  const [today, setToday] = useState(() => toCalendarDate(clock.now()));

  useEffect(() => {
    let timer: ReturnType<typeof setTimeout> | undefined;

    const refresh = () => {
      setToday(toCalendarDate(clock.now()));
      if (timer) clearTimeout(timer);
      // Small offset so the timer fires after midnight, not just before it.
      timer = setTimeout(refresh, msUntilNextDay(clock.now()) + 500);
    };

    refresh();
    const sub = AppState.addEventListener('change', (state) => {
      if (state === 'active') refresh();
    });

    return () => {
      if (timer) clearTimeout(timer);
      sub.remove();
    };
  }, [clock]);

  return today;
}
