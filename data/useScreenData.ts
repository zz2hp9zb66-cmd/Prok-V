import { useFocusEffect } from 'expo-router';
import { useCallback, useEffect, useRef, useState } from 'react';
import { useToday } from '@/services/time';
import type { DomainContext } from './context';
import { useServices } from './ServicesContext';

/**
 * Loads screen data from the local DB. Reloads when the screen gains focus
 * and when the calendar day changes (00:00 or returning to foreground, §27).
 */
export function useScreenData<T>(loader: (ctx: DomainContext) => Promise<T>) {
  const services = useServices();
  const today = useToday(services.clock);
  const [data, setData] = useState<T | null>(null);
  const loaderRef = useRef(loader);
  loaderRef.current = loader;

  const reload = useCallback(async () => {
    const result = await loaderRef.current(services);
    setData(result);
    return result;
  }, [services]);

  useFocusEffect(
    useCallback(() => {
      reload();
    }, [reload]),
  );

  // Day change while the screen stays open.
  const firstDay = useRef(today);
  useEffect(() => {
    if (today !== firstDay.current) reload();
  }, [today, reload]);

  return { data, reload, today, services };
}
