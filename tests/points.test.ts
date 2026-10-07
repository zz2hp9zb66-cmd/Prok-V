import { PointSourceType, PointTransactionType } from '@/data/db/schema';
import { pointTransactionsRepository } from '@/data/repositories/pointTransactionsRepository';
import { getBalance, recordPointTransaction } from '@/features/points/pointsService';
import { isDomainError } from '@/services/domainError';
import { createTestContext } from './helpers/testContext';

const accrual = (amount: number) => ({
  type: PointTransactionType.HabitCompletion,
  amount,
  sourceType: PointSourceType.HabitCompletion,
  sourceId: 'c1',
  titleSnapshot: 'Habit',
});

describe('points service', () => {
  it('starts at zero and sums transactions', async () => {
    const ctx = await createTestContext();
    expect(await getBalance(ctx.db)).toBe(0);
    await recordPointTransaction(ctx.db, ctx, accrual(10));
    await recordPointTransaction(ctx.db, ctx, accrual(5));
    expect(await getBalance(ctx.db)).toBe(15);
  });

  it('never allows a negative balance', async () => {
    const ctx = await createTestContext();
    await recordPointTransaction(ctx.db, ctx, accrual(10));
    const error = await recordPointTransaction(ctx.db, ctx, accrual(-11)).catch((e) => e);
    expect(isDomainError(error, 'insufficient_balance')).toBe(true);
    expect(await getBalance(ctx.db)).toBe(10);
  });

  it('rejects zero and fractional amounts', async () => {
    const ctx = await createTestContext();
    await expect(recordPointTransaction(ctx.db, ctx, accrual(0))).rejects.toThrow();
    await expect(recordPointTransaction(ctx.db, ctx, accrual(1.5))).rejects.toThrow();
  });

  it('stores time, local date, source and snapshot for every operation', async () => {
    const ctx = await createTestContext();
    await recordPointTransaction(ctx.db, ctx, accrual(3));
    const [t] = await pointTransactionsRepository.listAll(ctx.db);
    expect(t).toMatchObject({
      type: 'habit_completion',
      amount: 3,
      calendarDate: '2026-10-05',
      sourceType: 'habit_completion',
      sourceId: 'c1',
      titleSnapshot: 'Habit',
    });
    expect(t!.createdAt).toBe(ctx.clock.now().toISOString());
  });
});
