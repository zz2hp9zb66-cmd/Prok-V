import { useCallback, useEffect, useRef, useState } from 'react';
import type { TobiState } from './states';

/**
 * Temporarily switches TOBI to a reaction state, then back to `base`.
 * Purely visual: never awaited by business logic (§29).
 */
export function useTobiReaction(base: TobiState) {
  const [state, setState] = useState<TobiState>(base);
  const timer = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);

  const react = useCallback(
    (reaction: TobiState, durationMs = 1500) => {
      if (timer.current) clearTimeout(timer.current);
      setState(reaction);
      timer.current = setTimeout(() => setState(base), durationMs);
    },
    [base],
  );

  useEffect(
    () => () => {
      if (timer.current) clearTimeout(timer.current);
    },
    [],
  );
  return [state, react] as const;
}
