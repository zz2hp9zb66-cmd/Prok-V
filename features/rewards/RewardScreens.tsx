import { router, useLocalSearchParams } from 'expo-router';
import { useState } from 'react';
import { StyleSheet, View } from 'react-native';
import { AppText } from '@/components/AppText';
import { Card } from '@/components/Card';
import { ConfirmationModal } from '@/components/ConfirmationModal';
import { EmptyState } from '@/components/EmptyState';
import { PointsBadge } from '@/components/PointsBadge';
import { PrimaryButton } from '@/components/PrimaryButton';
import { ProgressBar } from '@/components/ProgressBar';
import { PanelHeading } from '@/components/PanelHeading';
import { REWARD_TYPE_LABEL } from '@/components/RewardCard';
import { RoomScreen } from '@/components/RoomScreen';
import { Screen } from '@/components/Screen';
import { SecondaryButton } from '@/components/SecondaryButton';
import { TOBIHero } from '@/components/TOBIHero';
import { useServices } from '@/data/ServicesContext';
import { RewardStatus, RewardType } from '@/data/db/schema';
import { useAction } from '@/data/useAction';
import { useScreenData } from '@/data/useScreenData';
import { formatDate, formatPoints } from '@/services/format';
import { spacing } from '@/theme';
import { getBalance } from '../points/pointsService';
import { useTobiReaction } from '../tobi/useTobiReaction';
import { RewardForm } from './RewardForm';
import { createReward, deleteReward, getReward, redeemReward, rewardProgress, updateReward } from './rewardsService';

function parseType(value: string | undefined): RewardType {
  return value === RewardType.Wish ? RewardType.Wish : RewardType.Goal;
}

export function RewardCreateScreen() {
  const type = parseType(useLocalSearchParams<{ type?: string }>().type);
  const services = useServices();
  const { busy, run } = useAction();
  return (
    <RoomScreen
      variant="form"
      tobiState={type === RewardType.Goal ? 'tobi_goal_create' : 'tobi_wish_create'}
      onBack={() => router.back()}
      bottomSafeArea
    >
      <PanelHeading title={type === RewardType.Goal ? 'Новая цель' : 'Новое желание'} />
      <RewardForm
        type={type}
        submitTitle={type === RewardType.Goal ? 'Создать цель' : 'Создать желание'}
        busy={busy}
        onSubmit={(input) =>
          run(async () => {
            await createReward(services, type, input);
            router.back();
          })
        }
      />
    </RoomScreen>
  );
}

/** Reward screen (§18): name, type, cost, balance/progress, status; edit / delete / redeem. */
export function RewardDetailsScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const { data, reload, services } = useScreenData(async (ctx) => ({
    reward: await getReward(ctx, id),
    balance: await getBalance(ctx.db),
  }));
  const { busy, run } = useAction();
  const [confirmDelete, setConfirmDelete] = useState(false);
  const [tobiState, reactTobi] = useTobiReaction('tobi_idle');

  if (!data) return null;
  const { reward, balance } = data;
  if (!reward) {
    return (
      <Screen edges={['bottom']}>
        <EmptyState title="Награда не найдена" />
      </Screen>
    );
  }

  const redeemed = reward.status === RewardStatus.Redeemed;
  const { progress, available } = rewardProgress(reward.cost, balance);

  // §13: no extra confirmation; the business event is saved before the animation.
  const redeem = () =>
    run(async () => {
      await redeemReward(services, reward.id);
      services.feedback.play('rewardRedeemed');
      reactTobi('tobi_reward', 2000);
      await reload();
    });

  return (
    <Screen edges={['bottom']}>
      <TOBIHero state={tobiState} size={150} />
      <AppText variant="caption" color="textSecondary">
        {REWARD_TYPE_LABEL[reward.type]}
      </AppText>
      <AppText variant="h1">{reward.name}</AppText>

      <Card>
        <View style={styles.row}>
          <AppText color="textSecondary">Стоимость</AppText>
          <AppText variant="bodyStrong">{formatPoints(reward.cost)}</AppText>
        </View>
        {redeemed ? (
          <AppText color="success" variant="bodyStrong">
            Получена {reward.redeemedAt ? formatDate(reward.redeemedAt) : ''}
          </AppText>
        ) : (
          <>
            <View style={styles.row}>
              <AppText color="textSecondary">Баланс</AppText>
              <PointsBadge value={balance} />
            </View>
            <ProgressBar progress={progress} color={available ? 'success' : 'primary'} />
            <AppText variant="caption" color={available ? 'success' : 'textSecondary'}>
              {available ? 'Можно получить' : `Ещё ${formatPoints(reward.cost - balance)}`}
            </AppText>
          </>
        )}
      </Card>

      {redeemed ? (
        <AppText color="textSecondary" align="center">
          Награда перенесена в архив.
        </AppText>
      ) : (
        <>
          <PrimaryButton title="Получить" onPress={redeem} disabled={!available || busy} />
          <SecondaryButton
            title="Редактировать"
            onPress={() => router.push({ pathname: '/reward/[id]/edit', params: { id: reward.id } })}
            disabled={busy}
          />
          <SecondaryButton title="Удалить" tone="danger" onPress={() => setConfirmDelete(true)} disabled={busy} />
        </>
      )}

      <ConfirmationModal
        visible={confirmDelete}
        title={reward.type === RewardType.Goal ? 'Удалить цель?' : 'Удалить желание?'}
        message="Баланс не изменится."
        confirmTitle="Удалить"
        destructive
        onCancel={() => setConfirmDelete(false)}
        onConfirm={() =>
          run(async () => {
            setConfirmDelete(false);
            await deleteReward(services, reward.id);
            router.back();
          })
        }
      />
    </Screen>
  );
}

export function RewardEditScreen() {
  const { id } = useLocalSearchParams<{ id: string }>();
  const { data, services } = useScreenData((ctx) => getReward(ctx, id));
  const { busy, run } = useAction();

  if (!data) return null;
  return (
    <Screen edges={['bottom']}>
      <RewardForm
        type={data.type}
        initial={{ name: data.name, cost: data.cost }}
        submitTitle="Сохранить"
        busy={busy}
        onSubmit={(input) =>
          run(async () => {
            await updateReward(services, id, input);
            router.back();
          })
        }
      />
    </Screen>
  );
}

const styles = StyleSheet.create({
  row: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', gap: spacing.sm },
});
