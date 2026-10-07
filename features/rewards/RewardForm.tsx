import { useState } from 'react';
import { StyleSheet, View } from 'react-native';
import { PointsInput } from '@/components/PointsInput';
import { PrimaryButton } from '@/components/PrimaryButton';
import { SecondaryButton } from '@/components/SecondaryButton';
import { TextInput } from '@/components/TextInput';
import { RewardType } from '@/data/db/schema';
import { spacing } from '@/theme';
import type { RewardInput } from './rewardsService';

export interface RewardFormProps {
  type: RewardType;
  initial?: RewardInput;
  submitTitle: string;
  onSubmit: (input: RewardInput) => void;
  secondary?: { title: string; onPress: () => void };
  busy?: boolean;
}

const PLACEHOLDER: Record<RewardType, string> = {
  [RewardType.Goal]: 'Например, поездка на море',
  [RewardType.Wish]: 'Например, любимый десерт',
};

export function RewardForm({ type, initial, submitTitle, onSubmit, secondary, busy }: RewardFormProps) {
  const [name, setName] = useState(initial?.name ?? '');
  const [cost, setCost] = useState<number | null>(initial?.cost ?? null);
  const [errors, setErrors] = useState<{ name?: string; cost?: string }>({});

  const submit = () => {
    const next: typeof errors = {};
    if (!name.trim()) next.name = 'Введи название';
    if (!cost || cost < 1) next.cost = 'Минимум 1 балл';
    setErrors(next);
    if (Object.keys(next).length > 0) return;
    onSubmit({ name, cost: cost! });
  };

  return (
    <View style={styles.form}>
      <TextInput label="Название" value={name} onChangeText={setName} error={errors.name} placeholder={PLACEHOLDER[type]} />
      <PointsInput label="Стоимость в баллах" value={cost} onChange={setCost} error={errors.cost} placeholder="100" />
      <PrimaryButton title={submitTitle} onPress={submit} disabled={busy} />
      {secondary ? <SecondaryButton title={secondary.title} onPress={secondary.onPress} disabled={busy} /> : null}
    </View>
  );
}

const styles = StyleSheet.create({
  form: { gap: spacing.sm },
});
