import { createContext, type ReactNode, useContext } from 'react';
import type { FeedbackService } from '@/services/feedback';
import type { DomainContext } from './context';

export interface AppServices extends DomainContext {
  feedback: FeedbackService;
}

const ServicesContext = createContext<AppServices | null>(null);

export function ServicesProvider({ value, children }: { value: AppServices; children: ReactNode }) {
  return <ServicesContext.Provider value={value}>{children}</ServicesContext.Provider>;
}

export function useServices(): AppServices {
  const services = useContext(ServicesContext);
  if (!services) throw new Error('useServices must be used inside <DataProvider>.');
  return services;
}
