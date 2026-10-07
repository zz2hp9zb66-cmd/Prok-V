import { useCallback, useRef, useState } from 'react';
import { Alert } from 'react-native';
import { isDomainError } from '@/services/domainError';
import { errorMessage } from '@/services/errorMessages';

/**
 * Runs a user action once at a time (guards double taps) and shows a
 * friendly message if a business rule rejects it.
 */
export function useAction() {
  const [busy, setBusy] = useState(false);
  const busyRef = useRef(false);

  const run = useCallback(async <T>(action: () => Promise<T>): Promise<T | undefined> => {
    if (busyRef.current) return undefined;
    busyRef.current = true;
    setBusy(true);
    try {
      return await action();
    } catch (error) {
      if (!isDomainError(error)) console.error(error);
      Alert.alert('TOBI Habit', errorMessage(error));
      return undefined;
    } finally {
      busyRef.current = false;
      setBusy(false);
    }
  }, []);

  return { busy, run };
}
