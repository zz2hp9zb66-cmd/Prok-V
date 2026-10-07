import { pointTransactionsRepository } from '@/data/repositories/pointTransactionsRepository';
import { completeHabit, createHabit } from '@/features/habits/habitsService';
import { getBalance } from '@/features/points/pointsService';
import {
  createReward,
  deleteReward,
  getReward,
  listActiveRewards,
  listArchive,
  redeemReward,
  rewardProgress,
  updateReward,
} from '@/features/rewards/rewardsService';
import { getStatistics } from '@/features/statistics/statisticsService';
import { isDomainError } from '@/services/domainError';
import { createTestContext } from './helpers/testContext';

const errorCode = (p: Promise<unknown>) => p.then(() => null, (e) => (isDomainError(e) ? e.code : e));

async function withBalance(points: number) {
  const ctx = await createTestContext();
  const habit = await createHabit(ctx, {
    name: 'Бег',
    weekdays: [0, 1, 2, 3, 4, 5, 6],
    pointsPerCompletion: points,
    dailyLimit: 1,
  });
  await completeHabit(ctx, habit.id);
  return ctx;
}

describe('rewards', () => {
  it('creates goals and wishes separately; duplicate names are allowed', async () => {
    const ctx = await createTestContext();
    await createReward(ctx, 'goal', { name: 'Поездка', cost: 500 });
    await createReward(ctx, 'goal', { name: 'Поездка', cost: 300 });
    await createReward(ctx, 'wish', { name: 'Кофе', cost: 20 });
    expect((await listActiveRewards(ctx, 'goal')).map((r) => r.name)).toEqual(['Поездка', 'Поездка']);
    expect((await listActiveRewards(ctx, 'wish')).map((r) => r.name)).toEqual(['Кофе']);
  });

  it('validates name and cost', async () => {
    const ctx = await createTestContext();
    expect(await errorCode(createReward(ctx, 'goal', { name: ' ', cost: 10 }))).toBe('validation');
    expect(await errorCode(createReward(ctx, 'goal', { name: 'X', cost: 0 }))).toBe('validation');
  });

  it('redeems when balance is enough: debit, status, date, archive', async () => {
    const ctx = await withBalance(100);
    const reward = await createReward(ctx, 'wish', { name: 'Кофе', cost: 30 });
    expect(rewardProgress(reward.cost, 100)).toEqual({ progress: 1, available: true });

    const redeemed = await redeemReward(ctx, reward.id);
    expect(redeemed).toMatchObject({ status: 'redeemed', redeemedAt: ctx.clock.now().toISOString() });
    expect(await getBalance(ctx.db)).toBe(70);
    expect(await listActiveRewards(ctx, 'wish')).toEqual([]);
    expect(await listArchive(ctx)).toEqual([expect.objectContaining({ id: reward.id, type: 'wish', cost: 30 })]);
    const txs = await pointTransactionsRepository.listAll(ctx.db);
    expect(txs.at(-1)).toMatchObject({ type: 'reward_redemption', amount: -30, sourceType: 'reward', sourceId: reward.id });
  });

  it('cannot redeem without enough points', async () => {
    const ctx = await withBalance(10);
    const reward = await createReward(ctx, 'goal', { name: 'Поездка', cost: 11 });
    expect(rewardProgress(reward.cost, 10).available).toBe(false);
    expect(await errorCode(redeemReward(ctx, reward.id))).toBe('insufficient_balance');
    expect((await getReward(ctx, reward.id))!.status).toBe('active');
    expect(await getBalance(ctx.db)).toBe(10);
  });

  it('redemption is final: cannot redeem, edit or delete again', async () => {
    const ctx = await withBalance(100);
    const reward = await createReward(ctx, 'goal', { name: 'Книга', cost: 50 });
    await redeemReward(ctx, reward.id);
    expect(await errorCode(redeemReward(ctx, reward.id))).toBe('reward_not_active');
    expect(await errorCode(updateReward(ctx, reward.id, { name: 'X', cost: 1 }))).toBe('reward_not_active');
    expect(await errorCode(deleteReward(ctx, reward.id))).toBe('reward_not_active');
    expect(await getBalance(ctx.db)).toBe(50);
    expect(await listArchive(ctx)).toHaveLength(1);
  });

  it('cost changes apply immediately and do not touch the balance', async () => {
    const ctx = await withBalance(50);
    const reward = await createReward(ctx, 'goal', { name: 'Книга', cost: 40 });
    const raised = await updateReward(ctx, reward.id, { name: 'Книга', cost: 60 });
    expect(rewardProgress(raised.cost, await getBalance(ctx.db)).available).toBe(false);
    expect(await getBalance(ctx.db)).toBe(50);
    expect(await errorCode(redeemReward(ctx, reward.id))).toBe('insufficient_balance');

    const lowered = await updateReward(ctx, reward.id, { name: 'Книга', cost: 45 });
    expect(rewardProgress(lowered.cost, 50).available).toBe(true);
    await redeemReward(ctx, reward.id);
    expect(await getBalance(ctx.db)).toBe(5);
  });

  it('deleting an unredeemed reward does not affect balance, statistics or archive', async () => {
    const ctx = await withBalance(30);
    const reward = await createReward(ctx, 'wish', { name: 'Кофе', cost: 10 });
    const before = await getStatistics(ctx);
    await deleteReward(ctx, reward.id);
    expect(await getReward(ctx, reward.id)).toBeNull();
    expect(await getBalance(ctx.db)).toBe(30);
    expect(await listArchive(ctx)).toEqual([]);
    expect(await getStatistics(ctx)).toEqual(before);
  });

  it('progress is partial below cost', () => {
    expect(rewardProgress(200, 50)).toEqual({ progress: 0.25, available: false });
  });
});
