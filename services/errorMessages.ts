import { isDomainError, type DomainErrorCode } from './domainError';

const MESSAGES: Record<DomainErrorCode, string> = {
  validation: 'Проверь заполненные поля.',
  not_found: 'Не удалось найти запись. Возможно, она уже удалена.',
  habit_not_scheduled_today: 'Сегодня эта привычка не запланирована.',
  habit_daily_limit_reached: 'На сегодня лимит выполнений достигнут.',
  completion_already_reversed: 'Это выполнение уже отменено.',
  completion_not_today: 'Можно отменить только сегодняшние выполнения.',
  insufficient_balance: 'Недостаточно баллов.',
  reward_not_active: 'Эта награда уже получена.',
};

export function errorMessage(error: unknown): string {
  if (isDomainError(error)) return MESSAGES[error.code];
  return 'Что-то пошло не так. Попробуй ещё раз.';
}
