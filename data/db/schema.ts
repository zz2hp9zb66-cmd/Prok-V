/**
 * Table and enum names shared by migrations and repositories (§25).
 */
export const PointTransactionType = {
  HabitCompletion: 'habit_completion',
  HabitCompletionReversal: 'habit_completion_reversal',
  RewardRedemption: 'reward_redemption',
} as const;
export type PointTransactionType = (typeof PointTransactionType)[keyof typeof PointTransactionType];

export const PointSourceType = {
  HabitCompletion: 'habit_completion',
  Reward: 'reward',
} as const;
export type PointSourceType = (typeof PointSourceType)[keyof typeof PointSourceType];

export const RewardType = {
  Goal: 'goal',
  Wish: 'wish',
} as const;
export type RewardType = (typeof RewardType)[keyof typeof RewardType];

export const RewardStatus = {
  Active: 'active',
  Redeemed: 'redeemed',
} as const;
export type RewardStatus = (typeof RewardStatus)[keyof typeof RewardStatus];
