import { useState } from 'react';
import { StyleSheet, View } from 'react-native';
import { AppText } from '@/components/AppText';
import { DaySelector } from '@/components/DaySelector';
import { PointsInput } from '@/components/PointsInput';
import { PrimaryButton } from '@/components/PrimaryButton';
import { SecondaryButton } from '@/components/SecondaryButton';
import { TextInput } from '@/components/TextInput';
import type { Weekday } from '@/services/time';
import { spacing } from '@/theme';
import type { HabitInput } from './habitRules';

export interface HabitFormProps {
  initial?: HabitInput;
  submitTitle: string;
  onSubmit: (input: HabitInput) => void;
  secondary?: { title: string; onPress: () => void };
  note?: string;
  busy?: boolean;
}

interface Errors {
  name?: string;
  weekdays?: string;
  points?: string;
  limit?: string;
}

export function HabitForm({ initial, submitTitle, onSubmit, secondary, note, busy }: HabitFormProps) {
  const [name, setName] = useState(initial?.name ?? '');
  const [weekdays, setWeekdays] = useState<Weekday[]>(initial ? [...initial.weekdays] : []);
  const [points, setPoints] = useState<number | null>(initial?.pointsPerCompletion ?? null);
  const [limit, setLimit] = useState<number | null>(initial?.dailyLimit ?? 1);
  const [errors, setErrors] = useState<Errors>({});

  const submit = () => {
    const next: Errors = {};
    if (!name.trim()) next.name = 'Введи название';
    if (weekdays.length === 0) next.weekdays = 'Выбери хотя бы один день';
    if (!points || points < 1) next.points = 'Минимум 1 балл';
    if (!limit || limit < 1) next.limit = 'Минимум 1 раз в день';
    setErrors(next);
    if (Object.keys(next).length > 0) return;
    onSubmit({ name, weekdays, pointsPerCompletion: points!, dailyLimit: limit! });
  };

  return (
    <View style={styles.form}>
      <TextInput label="Название" value={name} onChangeText={setName} error={errors.name} placeholder="Например, читать 20 минут" />
      <View style={styles.field}>
        <AppText variant="caption" color="textSecondary">
          Дни недели
        </AppText>
        <DaySelector value={weekdays} onChange={setWeekdays} />
        {errors.weekdays ? (
          <AppText variant="small" color="error">
            {errors.weekdays}
          </AppText>
        ) : null}
      </View>
      <PointsInput label="Баллы за выполнение" value={points} onChange={setPoints} error={errors.points} placeholder="10" />
      <PointsInput label="Лимит выполнений в день" value={limit} onChange={setLimit} error={errors.limit} />
      {note ? (
        <AppText variant="caption" color="info">
          {note}
        </AppText>
      ) : null}
      <PrimaryButton title={submitTitle} onPress={submit} disabled={busy} />
      {secondary ? <SecondaryButton title={secondary.title} onPress={secondary.onPress} disabled={busy} /> : null}
    </View>
  );
}

const styles = StyleSheet.create({
  form: { gap: spacing.sm },
  field: { gap: spacing.xxs },
});
