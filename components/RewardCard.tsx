import { StyleSheet, View } from 'react-native';
import { RewardType } from '@/data/db/schema';
import type { Reward } from '@/data/repositories/rewardsRepository';
import { rewardProgress } from '@/features/rewards/rewardsService';
import { formatDate, formatPoints } from '@/services/format';
import { spacing } from '@/theme';
import { AppText } from './AppText';
import { Card } from './Card';
import { ProgressBar } from './ProgressBar';

export const REWARD_TYPE_LABEL: Record<RewardType, string> = {
  [RewardType.Goal]: 'Цель',
  [RewardType.Wish]: 'Желание',
};

export interface RewardCardProps {
  reward: Reward;
  balance: number;
  onPress: () => void;
}

/** Active goal/wish: name, cost, progress, availability (§18). */
export function RewardCard({ reward, balance, onPress }: RewardCardProps) {
  const { progress, available } = rewardProgress(reward.cost, balance);
  return (
    <Card onPress={onPress} accessibilityLabel={reward.name}>
      <View style={styles.row}>
        <AppText variant="h3" style={styles.name} numberOfLines={2}>
          {reward.name}
        </AppText>
        <AppText variant="bodyStrong" color="accentDark">
          {formatPoints(reward.cost)}
        </AppText>
      </View>
      <ProgressBar progress={progress} color={available ? 'success' : 'primary'} />
      <AppText variant="caption" color={available ? 'success' : 'textSecondary'}>
        {available ? 'Можно получить' : `Ещё ${formatPoints(reward.cost - balance)}`}
      </AppText>
    </Card>
  );
}

/** Archive record: name, type, cost, redemption date (§14). Read-only. */
export function ArchivedRewardCard({ reward }: { reward: Reward }) {
  return (
    <Card>
      <View style={styles.row}>
        <AppText variant="h3" style={styles.name} numberOfLines={2}>
          {reward.name}
        </AppText>
        <AppText variant="bodyStrong" color="accentDark">
          {formatPoints(reward.cost)}
        </AppText>
      </View>
      <AppText variant="caption" color="textSecondary">
        {REWARD_TYPE_LABEL[reward.type]} · получена {reward.redeemedAt ? formatDate(reward.redeemedAt) : ''}
      </AppText>
    </Card>
  );
}

const styles = StyleSheet.create({
  row: { flexDirection: 'row', alignItems: 'flex-start', gap: spacing.xs },
  name: { flex: 1 },
});
