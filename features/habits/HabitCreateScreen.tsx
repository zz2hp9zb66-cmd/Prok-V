import { useState } from 'react';
import { Pressable, StyleSheet, View } from 'react-native';
import { AppText } from '@/components/AppText';
import { DaySelector } from '@/components/DaySelector';
import { Icon } from '@/components/Icon';
import { PointsInput } from '@/components/PointsInput';
import { PrimaryButton } from '@/components/PrimaryButton';
import { StepIndicator } from '@/components/StepIndicator';
import { TextInput } from '@/components/TextInput';
import { RoomScreen } from '@/components/RoomScreen';
import type { Weekday } from '@/services/time';
import { colors, radius, spacing } from '@/theme';
import { HABIT_CREATE_TOBI_SCALE, HABIT_CREATE_TOBI_VISIBLE } from './habitCreateTobi';
import type { HabitInput } from './habitRules';

/** UI limit for the task name (design requirement). */
export const HABIT_NAME_MAX_LENGTH = 60;

const COPY = {
  onboardingTitle: 'Давай создадим\nтвою задачу!',
  regularTitle: 'Новая задача',
  subtitle: 'Это может быть любая привычка, которая делает твою жизнь лучше. Тоби поможет не забывать о ней!',
  pointsHelp: 'Столько баллов ты получишь за каждое выполнение задачи.',
};

interface Errors {
  name?: string;
  points?: string;
  weekdays?: string;
  limit?: string;
}

export function validateHabitForm(input: {
  name: string;
  points: number | null;
  weekdays: readonly Weekday[];
  limit: number | null;
}): Errors {
  const errors: Errors = {};
  if (!input.name.trim()) errors.name = 'Введи название задачи';
  if (input.points === null || input.points < 1) errors.points = 'Укажи целое число баллов, минимум 1';
  if (input.weekdays.length === 0) errors.weekdays = 'Выбери хотя бы один день';
  if (input.limit === null || input.limit < 1) errors.limit = 'Минимум 1 раз в день';
  return errors;
}

export interface HabitCreateViewProps {
  /** Onboarding shows its step and title; regular creation does not. */
  step?: { current: number; total: number };
  onBack: () => void;
  onSubmit: (input: HabitInput) => void;
  /** Onboarding steps stay skippable (§5). */
  onSkip?: () => void;
  busy?: boolean;
}

/**
 * «Создание задачи» (design reference: task creation). Top — TOBI's room with
 * a slot for the TOBI render; bottom — cream panel with the form. The
 * «Продолжить» footer sits outside the scroll view so it stays reachable
 * above the keyboard.
 */
export function HabitCreateView({ step, onBack, onSubmit, onSkip, busy }: HabitCreateViewProps) {
  const [name, setName] = useState('');
  const [points, setPoints] = useState<number | null>(null);
  const [weekdays, setWeekdays] = useState<Weekday[]>([]);
  const [limit, setLimit] = useState<number | null>(1);
  const [errors, setErrors] = useState<Errors>({});
  const [showHelp, setShowHelp] = useState(false);

  const submit = () => {
    const next = validateHabitForm({ name, points, weekdays, limit });
    setErrors(next);
    if (Object.keys(next).length > 0) return;
    onSubmit({ name, weekdays, pointsPerCompletion: points!, dailyLimit: limit! });
  };

  return (
    <RoomScreen
      variant="form"
      tobiState="tobi_habit_create"
      // Head under the status bar, hoodie hem tucked behind the panel, notebook (≈94%) visible.
      characterScale={HABIT_CREATE_TOBI_SCALE}
      characterOffsetY={1 - HABIT_CREATE_TOBI_VISIBLE}
      onBack={onBack}
      footer={
        <>
          <PrimaryButton title="Продолжить" trailingIcon="arrow-forward-outline" onPress={submit} disabled={busy} />
          {onSkip ? (
            <Pressable accessibilityRole="button" onPress={onSkip} disabled={busy} style={styles.skip} hitSlop={8}>
              <AppText variant="bodyStrong" color="textSecondary">
                Пропустить
              </AppText>
            </Pressable>
          ) : null}
        </>
      }
    >
      {step ? <StepIndicator step={step.current} total={step.total} /> : null}
      <View style={styles.heading}>
        <AppText variant="h1" align="center" accessibilityRole="header">
          {step ? COPY.onboardingTitle : COPY.regularTitle}
        </AppText>
        <AppText color="textSecondary" align="center">
          {COPY.subtitle}
        </AppText>
      </View>

      <TextInput
        label="Название задачи"
        labelVariant="heading"
        placeholder="Например: Читать книгу"
        value={name}
        onChangeText={setName}
        maxLength={HABIT_NAME_MAX_LENGTH}
        showCounter
        error={errors.name}
        returnKeyType="next"
      />

      <PointsInput
        label="Стоимость задачи"
        labelVariant="heading"
        withStar
        placeholder="Напиши любое количество баллов"
        value={points}
        onChange={setPoints}
        error={errors.points}
        hint={showHelp ? COPY.pointsHelp : null}
        labelAccessory={
          <Pressable
            accessibilityRole="button"
            accessibilityLabel="Что такое стоимость задачи"
            accessibilityState={{ expanded: showHelp }}
            hitSlop={10}
            onPress={() => setShowHelp((v) => !v)}
            style={styles.help}
          >
            <Icon name="help-outline" size={18} color="textSecondary" />
          </Pressable>
        }
      />

      <View style={styles.field}>
        <AppText variant="h3">Повторение</AppText>
        <DaySelector value={weekdays} onChange={setWeekdays} />
        {errors.weekdays ? (
          <AppText variant="small" color="error">
            {errors.weekdays}
          </AppText>
        ) : null}
      </View>

      <PointsInput
        label="Лимит выполнений в день"
        labelVariant="heading"
        value={limit}
        onChange={setLimit}
        error={errors.limit}
      />
    </RoomScreen>
  );
}

const styles = StyleSheet.create({
  heading: { gap: spacing.xs },
  field: { gap: spacing.xs },
  help: {
    width: 26,
    height: 26,
    borderRadius: radius.pill,
    backgroundColor: colors.border,
    alignItems: 'center',
    justifyContent: 'center',
  },
  skip: { alignSelf: 'center', paddingVertical: spacing.xs },
});
