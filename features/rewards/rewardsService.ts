import type { DomainContext } from '@/data/context';
import { PointSourceType, PointTransactionType, RewardStatus, type RewardType } from '@/data/db/schema';
import type { SqlExecutor } from '@/data/db/types';
import { type Reward, rewardsRepository } from '@/data/repositories/rewardsRepository';
import { DomainError } from '@/services/domainError';
import { toTimestamp } from '@/services/time';
import { recordPointTransaction } from '../points/pointsService';

/** Goals and wishes share one mechanic (§12). */
export interface RewardInput {
  name: string;
  cost: number;
}

function validate(input: RewardInput): RewardInput {
  const name = input.name.trim();
  if (!name) throw new DomainError('validation', 'Reward name is required.');
  if (!Number.isInteger(input.cost) || input.cost < 1) throw new DomainError('validation', 'Cost must be an integer ≥ 1.');
  return { name, cost: input.cost };
}

async function getActiveReward(db: SqlExecutor, id: string): Promise<Reward> {
  const reward = await rewardsRepository.findById(db, id);
  if (!reward) throw new DomainError('not_found', 'Reward not found.');
  if (reward.status !== RewardStatus.Active) throw new DomainError('reward_not_active', 'Reward already redeemed.');
  return reward;
}

export async function createReward(ctx: DomainContext, type: RewardType, input: RewardInput): Promise<Reward> {
  const valid = validate(input);
  const now = toTimestamp(ctx.clock.now());
  const reward: Reward = {
    id: ctx.ids.next(),
    type,
    name: valid.name,
    cost: valid.cost,
    status: RewardStatus.Active,
    createdAt: now,
    updatedAt: now,
    redeemedAt: null,
  };
  await rewardsRepository.insert(ctx.db, reward);
  return reward;
}

/** Editable only before redemption; new cost applies immediately and does not touch the balance (§12). */
export async function updateReward(ctx: DomainContext, id: string, input: RewardInput): Promise<Reward> {
  const valid = validate(input);
  return ctx.db.transaction(async (tx) => {
    const reward = await getActiveReward(tx, id);
    const updated: Reward = { ...reward, ...valid, updatedAt: toTimestamp(ctx.clock.now()) };
    await rewardsRepository.update(tx, updated);
    return updated;
  });
}

/** Deleting an unredeemed reward affects neither balance, statistics nor archive (§12). */
export async function deleteReward(ctx: DomainContext, id: string): Promise<void> {
  await ctx.db.transaction(async (tx) => {
    await getActiveReward(tx, id);
    await rewardsRepository.delete(tx, id);
  });
}

/**
 * Redeems a reward (§13): debit + status + date in one atomic step. Final —
 * there is no way to cancel it.
 */
export async function redeemReward(ctx: DomainContext, id: string): Promise<Reward> {
  return ctx.db.transaction(async (tx) => {
    const reward = await getActiveReward(tx, id);
    // Throws insufficient_balance if there are not enough points.
    await recordPointTransaction(tx, ctx, {
      type: PointTransactionType.RewardRedemption,
      amount: -reward.cost,
      sourceType: PointSourceType.Reward,
      sourceId: reward.id,
      titleSnapshot: reward.name,
    });
    const now = toTimestamp(ctx.clock.now());
    const redeemed: Reward = { ...reward, status: RewardStatus.Redeemed, redeemedAt: now, updatedAt: now };
    await rewardsRepository.update(tx, redeemed);
    return redeemed;
  });
}

export function listActiveRewards(ctx: DomainContext, type: RewardType): Promise<Reward[]> {
  return rewardsRepository.listActiveByType(ctx.db, type);
}

export function listArchive(ctx: DomainContext): Promise<Reward[]> {
  return rewardsRepository.listRedeemed(ctx.db);
}

export function getReward(ctx: DomainContext, id: string): Promise<Reward | null> {
  return rewardsRepository.findById(ctx.db, id);
}

/** Progress toward a reward, 0..1, and whether it can be redeemed now. */
export function rewardProgress(cost: number, balance: number): { progress: number; available: boolean } {
  return { progress: Math.min(balance / cost, 1), available: balance >= cost };
}
