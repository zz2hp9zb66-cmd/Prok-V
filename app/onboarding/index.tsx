import { Redirect } from 'expo-router';

/** Onboarding starts with the goal step; the welcome is shown on cold start (`/`). */
export default function OnboardingIndex() {
  return <Redirect href="/onboarding/goal" />;
}
