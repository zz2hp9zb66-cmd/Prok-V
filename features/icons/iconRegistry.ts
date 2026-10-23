import type { ComponentProps } from 'react';
import type Ionicons from '@expo/vector-icons/Ionicons';
import type { ImageSourcePropType } from 'react-native';
import type { IconColorToken } from '@/theme';

/** Which kind of item an icon belongs to (decides the default icon). */
export type IconOwner = 'habit' | 'goal' | 'wish';

type IoniconName = ComponentProps<typeof Ionicons>['name'];

/**
 * Where the glyph comes from:
 *  - `vector` — a temporary Ionicons glyph;
 *  - `image` — a local PNG/WebP with transparency from `assets/icons/`,
 *    registered with a static `require` (Metro needs literal paths).
 */
export type IconGlyph = { kind: 'vector'; name: IoniconName } | { kind: 'image'; source: ImageSourcePropType };

export interface TobiIconDef {
  /** Stable id stored in SQLite. Never rename or reuse an id. */
  id: string;
  /** Russian label shown to the user. */
  label: string;
  glyph: IconGlyph;
  /** Background circle + glyph tint (tint is ignored for full-color images). */
  color: IconColorToken;
}

/**
 * Icon library (TOBI Icon Library v1, 70 icons), in picker order.
 * Images: `assets/icons/webp/<category>/<id>.webp` (1024×1024, transparent),
 * registered with static `require` (Metro needs literal paths).
 * The first five ids (sport, reading, water, language, sleep) existed before
 * as temporary glyphs — ids and labels are kept, so saved choices still work.
 * Never rename or reuse an id: SQLite stores only the id. See assets/icons/README.md.
 */
export const ICON_LIBRARY: readonly TobiIconDef[] = [
  // sport
  { id: 'sport', label: 'Спорт', glyph: { kind: 'image', source: require('@/assets/icons/webp/sport/sport.webp') }, color: 'sport' },
  { id: 'gym', label: 'Тренировка', glyph: { kind: 'image', source: require('@/assets/icons/webp/sport/gym.webp') }, color: 'sport' },
  { id: 'walking', label: 'Ходьба', glyph: { kind: 'image', source: require('@/assets/icons/webp/sport/walking.webp') }, color: 'sport' },
  { id: 'cycling', label: 'Велосипед', glyph: { kind: 'image', source: require('@/assets/icons/webp/sport/cycling.webp') }, color: 'sport' },
  { id: 'swimming', label: 'Плавание', glyph: { kind: 'image', source: require('@/assets/icons/webp/sport/swimming.webp') }, color: 'sport' },
  { id: 'yoga', label: 'Йога', glyph: { kind: 'image', source: require('@/assets/icons/webp/sport/yoga.webp') }, color: 'sport' },
  { id: 'football', label: 'Футбол', glyph: { kind: 'image', source: require('@/assets/icons/webp/sport/football.webp') }, color: 'sport' },
  { id: 'basketball', label: 'Баскетбол', glyph: { kind: 'image', source: require('@/assets/icons/webp/sport/basketball.webp') }, color: 'sport' },
  { id: 'hiking', label: 'Поход', glyph: { kind: 'image', source: require('@/assets/icons/webp/sport/hiking.webp') }, color: 'sport' },
  { id: 'medal', label: 'Достижение', glyph: { kind: 'image', source: require('@/assets/icons/webp/sport/medal.webp') }, color: 'sport' },
  // health
  { id: 'water', label: 'Вода', glyph: { kind: 'image', source: require('@/assets/icons/webp/health/water.webp') }, color: 'health' },
  { id: 'sleep', label: 'Сон', glyph: { kind: 'image', source: require('@/assets/icons/webp/health/sleep.webp') }, color: 'health' },
  { id: 'apple', label: 'Питание', glyph: { kind: 'image', source: require('@/assets/icons/webp/health/apple.webp') }, color: 'health' },
  { id: 'heart_health', label: 'Здоровье', glyph: { kind: 'image', source: require('@/assets/icons/webp/health/heart_health.webp') }, color: 'health' },
  { id: 'tooth', label: 'Зубы', glyph: { kind: 'image', source: require('@/assets/icons/webp/health/tooth.webp') }, color: 'health' },
  { id: 'meditation', label: 'Медитация', glyph: { kind: 'image', source: require('@/assets/icons/webp/health/meditation.webp') }, color: 'health' },
  { id: 'steps', label: 'Шаги', glyph: { kind: 'image', source: require('@/assets/icons/webp/health/steps.webp') }, color: 'health' },
  { id: 'sun', label: 'Солнце', glyph: { kind: 'image', source: require('@/assets/icons/webp/health/sun.webp') }, color: 'health' },
  { id: 'bath', label: 'Ванна', glyph: { kind: 'image', source: require('@/assets/icons/webp/health/bath.webp') }, color: 'health' },
  { id: 'medical', label: 'Забота о здоровье', glyph: { kind: 'image', source: require('@/assets/icons/webp/health/medical.webp') }, color: 'health' },
  // learning
  { id: 'reading', label: 'Чтение', glyph: { kind: 'image', source: require('@/assets/icons/webp/learning/reading.webp') }, color: 'learning' },
  { id: 'language', label: 'Языки', glyph: { kind: 'image', source: require('@/assets/icons/webp/learning/language.webp') }, color: 'learning' },
  { id: 'study', label: 'Учёба', glyph: { kind: 'image', source: require('@/assets/icons/webp/learning/study.webp') }, color: 'learning' },
  { id: 'writing', label: 'Письмо', glyph: { kind: 'image', source: require('@/assets/icons/webp/learning/writing.webp') }, color: 'learning' },
  { id: 'notes', label: 'Заметки', glyph: { kind: 'image', source: require('@/assets/icons/webp/learning/notes.webp') }, color: 'learning' },
  { id: 'brain', label: 'Мышление', glyph: { kind: 'image', source: require('@/assets/icons/webp/learning/brain.webp') }, color: 'learning' },
  { id: 'science', label: 'Наука', glyph: { kind: 'image', source: require('@/assets/icons/webp/learning/science.webp') }, color: 'learning' },
  { id: 'math', label: 'Математика', glyph: { kind: 'image', source: require('@/assets/icons/webp/learning/math.webp') }, color: 'learning' },
  { id: 'coding', label: 'Программирование', glyph: { kind: 'image', source: require('@/assets/icons/webp/learning/coding.webp') }, color: 'learning' },
  { id: 'library', label: 'Книга', glyph: { kind: 'image', source: require('@/assets/icons/webp/learning/library.webp') }, color: 'learning' },
  // work
  { id: 'work', label: 'Работа', glyph: { kind: 'image', source: require('@/assets/icons/webp/work/work.webp') }, color: 'work' },
  { id: 'computer', label: 'Компьютер', glyph: { kind: 'image', source: require('@/assets/icons/webp/work/computer.webp') }, color: 'work' },
  { id: 'calendar', label: 'Планирование', glyph: { kind: 'image', source: require('@/assets/icons/webp/work/calendar.webp') }, color: 'work' },
  { id: 'clock', label: 'Время', glyph: { kind: 'image', source: require('@/assets/icons/webp/work/clock.webp') }, color: 'work' },
  { id: 'checklist', label: 'Список дел', glyph: { kind: 'image', source: require('@/assets/icons/webp/work/checklist.webp') }, color: 'work' },
  { id: 'target', label: 'Цель', glyph: { kind: 'image', source: require('@/assets/icons/webp/work/target.webp') }, color: 'work' },
  { id: 'email', label: 'Почта', glyph: { kind: 'image', source: require('@/assets/icons/webp/work/email.webp') }, color: 'work' },
  { id: 'meeting', label: 'Встреча', glyph: { kind: 'image', source: require('@/assets/icons/webp/work/meeting.webp') }, color: 'work' },
  { id: 'idea', label: 'Идея', glyph: { kind: 'image', source: require('@/assets/icons/webp/work/idea.webp') }, color: 'work' },
  { id: 'project', label: 'Проект', glyph: { kind: 'image', source: require('@/assets/icons/webp/work/project.webp') }, color: 'work' },
  // finance
  { id: 'money', label: 'Деньги', glyph: { kind: 'image', source: require('@/assets/icons/webp/finance/money.webp') }, color: 'finance' },
  { id: 'saving', label: 'Накопления', glyph: { kind: 'image', source: require('@/assets/icons/webp/finance/saving.webp') }, color: 'finance' },
  { id: 'bank', label: 'Банк', glyph: { kind: 'image', source: require('@/assets/icons/webp/finance/bank.webp') }, color: 'finance' },
  { id: 'chart', label: 'Рост', glyph: { kind: 'image', source: require('@/assets/icons/webp/finance/chart.webp') }, color: 'finance' },
  { id: 'gift', label: 'Подарок', glyph: { kind: 'image', source: require('@/assets/icons/webp/finance/gift.webp') }, color: 'finance' },
  { id: 'shopping', label: 'Покупки', glyph: { kind: 'image', source: require('@/assets/icons/webp/finance/shopping.webp') }, color: 'finance' },
  { id: 'coins', label: 'Монеты', glyph: { kind: 'image', source: require('@/assets/icons/webp/finance/coins.webp') }, color: 'finance' },
  { id: 'house', label: 'Дом', glyph: { kind: 'image', source: require('@/assets/icons/webp/finance/house.webp') }, color: 'finance' },
  { id: 'car', label: 'Автомобиль', glyph: { kind: 'image', source: require('@/assets/icons/webp/finance/car.webp') }, color: 'finance' },
  { id: 'receipt', label: 'Расходы', glyph: { kind: 'image', source: require('@/assets/icons/webp/finance/receipt.webp') }, color: 'finance' },
  // life
  { id: 'travel', label: 'Путешествие', glyph: { kind: 'image', source: require('@/assets/icons/webp/life/travel.webp') }, color: 'life' },
  { id: 'globe', label: 'Мир', glyph: { kind: 'image', source: require('@/assets/icons/webp/life/globe.webp') }, color: 'life' },
  { id: 'coffee', label: 'Кофе', glyph: { kind: 'image', source: require('@/assets/icons/webp/life/coffee.webp') }, color: 'life' },
  { id: 'cooking', label: 'Готовка', glyph: { kind: 'image', source: require('@/assets/icons/webp/life/cooking.webp') }, color: 'life' },
  { id: 'cleaning', label: 'Уборка', glyph: { kind: 'image', source: require('@/assets/icons/webp/life/cleaning.webp') }, color: 'life' },
  { id: 'plant', label: 'Растения', glyph: { kind: 'image', source: require('@/assets/icons/webp/life/plant.webp') }, color: 'life' },
  { id: 'pet', label: 'Питомец', glyph: { kind: 'image', source: require('@/assets/icons/webp/life/pet.webp') }, color: 'life' },
  { id: 'music', label: 'Музыка', glyph: { kind: 'image', source: require('@/assets/icons/webp/life/music.webp') }, color: 'life' },
  { id: 'camera', label: 'Фото', glyph: { kind: 'image', source: require('@/assets/icons/webp/life/camera.webp') }, color: 'life' },
  { id: 'art', label: 'Творчество', glyph: { kind: 'image', source: require('@/assets/icons/webp/life/art.webp') }, color: 'life' },
  { id: 'friends', label: 'Друзья', glyph: { kind: 'image', source: require('@/assets/icons/webp/life/friends.webp') }, color: 'life' },
  { id: 'love', label: 'Любовь', glyph: { kind: 'image', source: require('@/assets/icons/webp/life/love.webp') }, color: 'life' },
  { id: 'family', label: 'Семья', glyph: { kind: 'image', source: require('@/assets/icons/webp/life/family.webp') }, color: 'life' },
  { id: 'star', label: 'Желание', glyph: { kind: 'image', source: require('@/assets/icons/webp/life/star.webp') }, color: 'life' },
  { id: 'trophy', label: 'Победа', glyph: { kind: 'image', source: require('@/assets/icons/webp/life/trophy.webp') }, color: 'life' },
  { id: 'movie', label: 'Кино', glyph: { kind: 'image', source: require('@/assets/icons/webp/life/movie.webp') }, color: 'life' },
  { id: 'game', label: 'Игры', glyph: { kind: 'image', source: require('@/assets/icons/webp/life/game.webp') }, color: 'life' },
  { id: 'vinyl', label: 'Винил', glyph: { kind: 'image', source: require('@/assets/icons/webp/life/vinyl.webp') }, color: 'life' },
  { id: 'nature', label: 'Природа', glyph: { kind: 'image', source: require('@/assets/icons/webp/life/nature.webp') }, color: 'life' },
  { id: 'celebration', label: 'Праздник', glyph: { kind: 'image', source: require('@/assets/icons/webp/life/celebration.webp') }, color: 'life' },
];

/** Universal per-type icons: used when nothing was chosen or the id is unknown. */
export const DEFAULT_ICONS: Readonly<Record<IconOwner, TobiIconDef>> = {
  habit: { id: 'default_habit', label: 'Привычка', glyph: { kind: 'vector', name: 'checkmark-done-outline' }, color: 'amber' },
  goal: { id: 'default_goal', label: 'Цель', glyph: { kind: 'vector', name: 'flag-outline' }, color: 'peach' },
  wish: { id: 'default_wish', label: 'Желание', glyph: { kind: 'vector', name: 'gift-outline' }, color: 'rose' },
};

const BY_ID = new Map<string, TobiIconDef>(
  [...ICON_LIBRARY, ...Object.values(DEFAULT_ICONS)].map((icon) => [icon.id, icon]),
);

/** Icons offered in the picker for an item type: its default first, then the library. */
export function pickerIcons(owner: IconOwner): TobiIconDef[] {
  return [DEFAULT_ICONS[owner], ...ICON_LIBRARY];
}

/** Resolves a stored id; null/unknown ids fall back to the type's default (never throws). */
export function resolveIcon(iconId: string | null | undefined, owner: IconOwner): TobiIconDef {
  return (iconId && BY_ID.get(iconId)) || DEFAULT_ICONS[owner];
}

export function defaultIconId(owner: IconOwner): string {
  return DEFAULT_ICONS[owner].id;
}
