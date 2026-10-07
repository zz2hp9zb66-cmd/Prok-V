import { router } from 'expo-router';
import { useState } from 'react';
import { EmptyState } from '@/components/EmptyState';
import { ArchivedRewardCard, RewardCard } from '@/components/RewardCard';
import { Screen } from '@/components/Screen';
import { SectionHeader } from '@/components/SectionHeader';
import { SegmentedControl } from '@/components/SegmentedControl';
import { TOBIHeader } from '@/components/TOBIHeader';
import { RewardType } from '@/data/db/schema';
import { useScreenData } from '@/data/useScreenData';
import { getBalance } from '../points/pointsService';
import { listActiveRewards, listArchive } from './rewardsService';

type Tab = 'goal' | 'wish' | 'archive';

const TABS = [
  { value: 'goal', label: 'Цели' },
  { value: 'wish', label: 'Желания' },
  { value: 'archive', label: 'Архив' },
] as const;

const EMPTY: Record<Tab, { title: string; description: string }> = {
  goal: { title: 'Пока нет целей', description: 'Цель — что-то важное, ради чего стоит копить баллы.' },
  wish: { title: 'Пока нет желаний', description: 'Желание — небольшая радость за твои усилия.' },
  archive: { title: 'Архив пуст', description: 'Здесь появятся полученные цели и желания.' },
};

/** «Награды» (§18): TOBI + balance; tabs Цели / Желания / Архив. */
export function RewardsScreen() {
  const [tab, setTab] = useState<Tab>('goal');
  const { data } = useScreenData(async (ctx) => ({
    balance: await getBalance(ctx.db),
    goals: await listActiveRewards(ctx, RewardType.Goal),
    wishes: await listActiveRewards(ctx, RewardType.Wish),
    archive: await listArchive(ctx),
  }));

  const balance = data?.balance ?? 0;
  const items = tab === 'goal' ? data?.goals : tab === 'wish' ? data?.wishes : data?.archive;
  // Contextual creation (§6): «+» only in goals and wishes, never in the archive.
  const onAdd = tab === 'archive' ? undefined : () => router.push({ pathname: '/reward/new', params: { type: tab } });

  return (
    <Screen>
      <TOBIHeader tobiState="tobi_idle" title="Награды" subtitle="Копи баллы на то, что важно." balance={balance} />
      <SegmentedControl options={TABS} value={tab} onChange={setTab} />
      <SectionHeader
        title={TABS.find((t) => t.value === tab)!.label}
        onAdd={onAdd}
        addLabel={tab === 'goal' ? 'Создать цель' : 'Создать желание'}
      />
      {items && items.length === 0 ? (
        <EmptyState
          {...EMPTY[tab]}
          actionTitle={onAdd ? (tab === 'goal' ? 'Создать цель' : 'Создать желание') : undefined}
          onAction={onAdd}
        />
      ) : null}
      {items?.map((reward) =>
        tab === 'archive' ? (
          <ArchivedRewardCard key={reward.id} reward={reward} />
        ) : (
          <RewardCard
            key={reward.id}
            reward={reward}
            balance={balance}
            onPress={() => router.push({ pathname: '/reward/[id]', params: { id: reward.id } })}
          />
        ),
      )}
    </Screen>
  );
}
