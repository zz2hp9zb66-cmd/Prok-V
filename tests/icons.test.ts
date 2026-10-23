import { migrate, migrations } from '@/data/db/migrations';
import { habitsRepository } from '@/data/repositories/habitsRepository';
import { rewardsRepository } from '@/data/repositories/rewardsRepository';
import { createHabit, updateHabit } from '@/features/habits/habitsService';
import { DEFAULT_ICONS, ICON_LIBRARY, pickerIcons, resolveIcon } from '@/features/icons/iconRegistry';
import { getBalance } from '@/features/points/pointsService';
import { createReward, updateReward } from '@/features/rewards/rewardsService';
import { createTestContext } from './helpers/testContext';
import { createTestDatabase } from './helpers/testDatabase';

const habit = { name: 'Бег', weekdays: [0, 1, 2, 3, 4, 5, 6] as const, pointsPerCompletion: 10, dailyLimit: 1 };

describe('icon registry', () => {
  it('has the five temporary icons with stable ids and unique ids overall', () => {
    expect(ICON_LIBRARY.map((i) => i.id)).toEqual(['sport', 'reading', 'water', 'language', 'sleep']);
    const all = [...ICON_LIBRARY, ...Object.values(DEFAULT_ICONS)].map((i) => i.id);
    expect(new Set(all).size).toBe(all.length);
  });

  it('falls back to the type default for null and unknown ids', () => {
    expect(resolveIcon(null, 'habit').id).toBe('default_habit');
    expect(resolveIcon(undefined, 'goal').id).toBe('default_goal');
    expect(resolveIcon('deleted-icon', 'wish').id).toBe('default_wish');
    expect(resolveIcon('water', 'wish').id).toBe('water');
  });

  it('offers the type default first, then the library', () => {
    expect(pickerIcons('goal').map((i) => i.id)).toEqual(['default_goal', 'sport', 'reading', 'water', 'language', 'sleep']);
  });
});

describe('icon persistence', () => {
  it('migration v2 keeps existing records and leaves their icon empty', async () => {
    const db = createTestDatabase();
    await db.execAsync(migrations[0]!);
    await db.execAsync('PRAGMA user_version = 1');
    const now = new Date().toISOString();
    await db.runAsync(
      'INSERT INTO habits (id, name, selected_weekdays, points_per_completion, daily_limit, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)',
      ['h1', 'Старая привычка', 127, 5, 1, now, now],
    );
    await db.runAsync(
      "INSERT INTO rewards (id, type, name, cost, status, created_at, updated_at) VALUES ('r1', 'goal', 'Старая цель', 50, 'active', ?, ?)",
      [now, now],
    );
    await db.runAsync(
      "INSERT INTO point_transactions (id, type, amount, created_at, calendar_date, source_type, source_id, title_snapshot) VALUES ('t1', 'habit_completion', 5, ?, '2026-10-01', 'habit_completion', 'c1', 'x')",
      [now],
    );

    await migrate(db);

    expect(await habitsRepository.findById(db, 'h1')).toMatchObject({ name: 'Старая привычка', iconId: null });
    expect(await rewardsRepository.findById(db, 'r1')).toMatchObject({ name: 'Старая цель', iconId: null });
    expect(await getBalance(db)).toBe(5);
    expect(resolveIcon(null, 'habit').id).toBe('default_habit'); // shown as the default icon
  });

  it('habits: default icon when not chosen, chosen icon saved, changed on edit, kept when omitted', async () => {
    const ctx = await createTestContext();
    const plain = await createHabit(ctx, { ...habit, weekdays: [...habit.weekdays] });
    expect(plain.iconId).toBe('default_habit');

    const chosen = await createHabit(ctx, { ...habit, weekdays: [...habit.weekdays], iconId: 'sport' });
    expect((await habitsRepository.findById(ctx.db, chosen.id))!.iconId).toBe('sport');

    await updateHabit(ctx, chosen.id, { ...habit, weekdays: [...habit.weekdays], iconId: 'water' });
    expect((await habitsRepository.findById(ctx.db, chosen.id))!.iconId).toBe('water');

    await updateHabit(ctx, chosen.id, { ...habit, name: 'Бег утром', weekdays: [...habit.weekdays] });
    expect((await habitsRepository.findById(ctx.db, chosen.id))!).toMatchObject({ name: 'Бег утром', iconId: 'water' });
  });

  it('goals and wishes: default per type, chosen icon saved and changed, cost and balance untouched', async () => {
    const ctx = await createTestContext();
    expect((await createReward(ctx, 'goal', { name: 'Кино', cost: 50 })).iconId).toBe('default_goal');
    expect((await createReward(ctx, 'wish', { name: 'Кофе', cost: 5 })).iconId).toBe('default_wish');

    const wish = await createReward(ctx, 'wish', { name: 'Книга', cost: 30, iconId: 'reading' });
    await updateReward(ctx, wish.id, { name: 'Книга', cost: 30, iconId: 'sleep' });
    expect(await rewardsRepository.findById(ctx.db, wish.id)).toMatchObject({ iconId: 'sleep', cost: 30, status: 'active' });
    await updateReward(ctx, wish.id, { name: 'Новая книга', cost: 40 });
    expect(await rewardsRepository.findById(ctx.db, wish.id)).toMatchObject({ name: 'Новая книга', iconId: 'sleep' });
    expect(await getBalance(ctx.db)).toBe(0);
  });
});
