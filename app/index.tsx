import { Redirect } from 'expo-router';
import { useEffect, useState } from 'react';
import { useServices } from '@/data/DataProvider';
import { settingsRepository } from '@/data/repositories/settingsRepository';

/** Launch gate (§5–6): onboarding on first launch, otherwise always «Задачи». */
export default function Index() {
  const { db } = useServices();
  const [onboardingCompleted, setOnboardingCompleted] = useState<boolean | null>(null);

  useEffect(() => {
    settingsRepository.isOnboardingCompleted(db).then(setOnboardingCompleted);
  }, [db]);

  if (onboardingCompleted === null) return null;
  return <Redirect href={onboardingCompleted ? '/tasks' : '/onboarding'} />;
}
