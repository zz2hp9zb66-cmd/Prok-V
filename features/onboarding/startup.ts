/**
 * Launch flow (owner decision D14): on every cold start the welcome screen is
 * shown for 3 s, then the user goes to onboarding (first launch) or «Задачи».
 * The only source of truth is the persisted `onboardingCompleted` setting —
 * never the presence of habits.
 */
export const WELCOME_SPLASH_MS = 3000;

export type StartupDestination = '/onboarding/goal' | '/tasks';

export function startupDestination(onboardingCompleted: boolean): StartupDestination {
  return onboardingCompleted ? '/tasks' : '/onboarding/goal';
}
