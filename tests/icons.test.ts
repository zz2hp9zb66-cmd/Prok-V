import fs from 'node:fs';
import path from 'node:path';
import { migrate, migrations } from '@/data/db/migrations';
import { habitsRepository } from '@/data/repositories/habitsRepository';
import { rewardsRepository } from '@/data/repositories/rewardsRepository';
import { createHabit, updateHabit } from '@/features/habits/habitsService';
import { DEFAULT_ICONS, ICON_LIBRARY, pickerIcons, resolveIcon } from '@/features/icons/iconRegistry';
import { getBalance } from '@/features/points/pointsService';
import { createReward, updateReward } from '@/features/rewards/rewardsService';
import { iconColors } from '@/theme/colors';
import { createTestContext } from './helpers/testContext';
import { createTestDatabase } from './helpers/testDatabase';

/** Reads width, height and alpha flag from a WebP header (VP8L or VP8X), no dependencies. */
function readWebpInfo(buf: Buffer): { width: number; height: number; alpha: boolean } {
  if (buf.toString('ascii', 0, 4) !== 'RIFF' || buf.toString('ascii', 8, 12) !== 'WEBP') throw new Error('not a WebP file');
  const chunk = buf.toString('ascii', 12, 16);
  if (chunk === 'VP8L') {
    const bits = buf.readUInt32LE(21);
    return { width: (bits & 0x3fff) + 1, height: ((bits >> 14) & 0x3fff) + 1, alpha: ((bits >> 28) & 1) === 1 };
  }
  if (chunk === 'VP8X') {
    const w = buf.readUIntLE(24, 3) + 1;
    const h = buf.readUIntLE(27, 3) + 1;
    return { width: w, height: h, alpha: (buf[20]! & 0x10) !== 0 };
  }
  throw new Error(`unsupported WebP chunk ${chunk}`);
}

const habit = { name: 'Бег', weekdays: [0, 1, 2, 3, 4, 5, 6] as const, pointsPerCompletion: 10, dailyLimit: 1 };

describe('icon registry', () => {
  const manifest = JSON.parse(
    fs.readFileSync(path.join(__dirname, '../assets/icons/manifest.json'), 'utf8'),
  ) as { items: { id: string; category: string; webp: string; size: number[] }[] };

  it('contains all 70 icons of TOBI Icon Library v1, in manifest order, with unique ids', () => {
    expect(manifest.items).toHaveLength(70);
    expect(ICON_LIBRARY.map((i) => i.id)).toEqual(manifest.items.map((i) => i.id));
    const all = [...ICON_LIBRARY, ...Object.values(DEFAULT_ICONS)].map((i) => i.id);
    expect(new Set(all).size).toBe(all.length);
  });

  it('keeps the ids and labels of the five former temporary icons', () => {
    const byId = new Map(ICON_LIBRARY.map((i) => [i.id, i]));
    expect(
      ['sport', 'reading', 'water', 'language', 'sleep'].map((id) => [id, byId.get(id)?.label]),
    ).toEqual([
      ['sport', 'Спорт'],
      ['reading', 'Чтение'],
      ['water', 'Вода'],
      ['language', 'Языки'],
      ['sleep', 'Сон'],
    ]);
  });

  it('uses a local image file for every library icon and the category background', () => {
    for (const item of manifest.items) {
      const icon = ICON_LIBRARY.find((i) => i.id === item.id)!;
      expect(icon.glyph.kind).toBe('image');
      expect(icon.color).toBe(item.category);
      expect(iconColors[icon.color]).toBeDefined();
      expect(fs.existsSync(path.join(__dirname, '../assets/icons', item.webp))).toBe(true);
      expect(item.size).toEqual([256, 256]);
    }
  });

  it('every library file is a 256×256 WebP with an alpha channel', () => {
    for (const item of manifest.items) {
      const info = readWebpInfo(fs.readFileSync(path.join(__dirname, '../assets/icons', item.webp)));
      expect({ id: item.id, ...info }).toEqual({ id: item.id, width: 256, height: 256, alpha: true });
    }
  });

  it('keeps the default icons per type unchanged', () => {
    expect(Object.values(DEFAULT_ICONS).map((i) => [i.id, i.glyph.kind])).toEqual([
      ['default_habit', 'vector'],
      ['default_goal', 'vector'],
      ['default_wish', 'vector'],
    ]);
  });

  it('falls back to the type default for null and unknown ids', () => {
    expect(resolveIcon(null, 'habit').id).toBe('default_habit');
    expect(resolveIcon(undefined, 'goal').id).toBe('default_goal');
    expect(resolveIcon('deleted-icon', 'wish').id).toBe('default_wish');
    expect(resolveIcon('water', 'wish').id).toBe('water');
  });

  it('offers the type default first, then the library', () => {
    const ids = pickerIcons('goal').map((i) => i.id);
    expect(ids).toHaveLength(71);
    expect(ids.slice(0, 3)).toEqual(['default_goal', 'sport', 'gym']);
    expect(ids.at(-1)).toBe('celebration');
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
