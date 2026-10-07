import type { DomainContext } from '@/data/context';
import type { PointSourceType, PointTransactionType } from '@/data/db/schema';
import type { SqlExecutor } from '@/data/db/types';
import { type PointTransaction, pointTransactionsRepository } from '@/data/repositories/pointTransactionsRepository';
import { DomainError } from '@/services/domainError';
import { toCalendarDate, toTimestamp } from '@/services/time';

/**
 * The only place where the balance changes (§26). Balance = sum of all point
 * transactions; it is never stored separately and never goes below 0 (§15).
 */
export async function getBalance(db: SqlExecutor): Promise<number> {
  return pointTransactionsRepository.sumAll(db);
}

export interface PointTransactionInput {
  type: PointTransactionType;
  amount: number;
  sourceType: PointSourceType;
  sourceId: string;
  titleSnapshot: string;
}

/**
 * Records a balance change. Must be called inside the caller's transaction
 * together with the related business change, so both commit atomically.
 * Throws `insufficient_balance` if the resulting balance would be negative.
 */
export async function recordPointTransaction(
  tx: SqlExecutor,
  ctx: Pick<DomainContext, 'clock' | 'ids'>,
  input: PointTransactionInput,
): Promise<PointTransaction> {
  if (!Number.isInteger(input.amount) || input.amount === 0) {
    throw new DomainError('validation', 'Point amount must be a non-zero integer.');
  }
  const balance = await getBalance(tx);
  if (balance + input.amount < 0) {
    throw new DomainError('insufficient_balance', 'Balance cannot become negative.');
  }
  const now = ctx.clock.now();
  const transaction: PointTransaction = {
    id: ctx.ids.next(),
    createdAt: toTimestamp(now),
    calendarDate: toCalendarDate(now),
    ...input,
  };
  await pointTransactionsRepository.insert(tx, transaction);
  return transaction;
}
