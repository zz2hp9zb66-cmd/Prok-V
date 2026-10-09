import { router } from 'expo-router';
import { useEffect, useRef, useState } from 'react';
import { useServices } from '@/data/ServicesContext';
import { settingsRepository } from '@/data/repositories/settingsRepository';
import { type StartupDestination, startupDestination, WELCOME_SPLASH_MS } from './startup';
import { WelcomeScreen } from './WelcomeScreen';

/**
 * Cold-start screen (`/`). Shows the welcome screen for WELCOME_SPLASH_MS,
 * reads `onboardingCompleted` in parallel and then replaces the route once:
 * onboarding for a new user, «Задачи» for an existing one. Waits for the
 * setting if it is still loading when the time is up. The route is only
 * mounted on a cold start, so returning from background or switching tabs
 * never shows it again.
 */
export function StartupScreen() {
  const { db } = useServices();
  const [destination, setDestination] = useState<StartupDestination | null>(null);
  const [readError, setReadError] = useState<unknown>(null);
  const [timeUp, setTimeUp] = useState(false);
  const navigated = useRef(false);

  // Read the persisted onboarding state (DB is already open and migrated here).
  useEffect(() => {
    let alive = true;
    settingsRepository.isOnboardingCompleted(db).then(
      (completed) => alive && setDestination(startupDestination(completed)),
      (error) => alive && setReadError(error),
    );
    return () => {
      alive = false;
    };
  }, [db]);

  // One timer per mount, started once the screen is committed; cleared on unmount.
  useEffect(() => {
    const timer = setTimeout(() => setTimeUp(true), WELCOME_SPLASH_MS);
    return () => clearTimeout(timer);
  }, []);

  useEffect(() => {
    if (!timeUp || !destination || navigated.current) return;
    navigated.current = true;
    // `replace`: «Назад» never returns to the welcome screen.
    router.replace(destination);
  }, [timeUp, destination]);

  // Reading failed: hand over to the root ErrorBoundary (retry). No data is touched.
  if (readError) throw readError;

  return <WelcomeScreen onStart={null} />;
}
