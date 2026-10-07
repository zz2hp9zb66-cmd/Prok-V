import { randomUUID } from 'expo-crypto';

/** ID generator; injectable so domain logic stays testable outside React Native. */
export interface IdGenerator {
  next(): string;
}

export const uuidGenerator: IdGenerator = {
  next: () => randomUUID(),
};
