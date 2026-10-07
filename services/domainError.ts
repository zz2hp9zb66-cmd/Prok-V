/**
 * Expected business-rule violations. UI maps `code` to a user message;
 * anything else is a real bug.
 */
export type DomainErrorCode =
  | 'validation'
  | 'not_found'
  | 'habit_not_scheduled_today'
  | 'habit_daily_limit_reached'
  | 'completion_already_reversed'
  | 'completion_not_today'
  | 'insufficient_balance'
  | 'reward_not_active';

export class DomainError extends Error {
  constructor(
    readonly code: DomainErrorCode,
    message: string,
  ) {
    super(message);
    this.name = 'DomainError';
  }
}

export function isDomainError(error: unknown, code?: DomainErrorCode): error is DomainError {
  return error instanceof DomainError && (code === undefined || error.code === code);
}
