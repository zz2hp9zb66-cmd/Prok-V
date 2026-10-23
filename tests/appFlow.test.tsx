import { act, fireEvent, renderRouter, screen, waitFor } from 'expo-router/testing-library';
import { settingsRepository } from '@/data/repositories/settingsRepository';
import type { AppServices } from '@/data/ServicesContext';
import { completeHabit, createHabit } from '@/features/habits/habitsService';
import { createReward, getReward } from '@/features/rewards/rewardsService';
import { TOBI_ROOM_SHARED } from '@/features/tobi/tobiAssets';
import { noopFeedback } from '@/services/feedback';
import { createTestContext, type FakeClock } from './helpers/testContext';

/**
 * End-to-end UI flow over the real routes in `app/` with an in-memory
 * database (Definition of Done §35). The DB survives re-renders, which
 * stands in for closing and reopening the app.
 */
let mockServices: AppServices & { clock: FakeClock };

jest.mock('@/data/DataProvider', () => {
  const { ServicesProvider } = jest.requireActual('@/data/ServicesContext');
  return {
    DataProvider: ({ children }: { children: React.ReactNode }) => (
      <ServicesProvider value={mockServices}>{children}</ServicesProvider>
    ),
  };
});

jest.mock('@expo/vector-icons/Ionicons', () => 'Ionicons');

// Animations are visual only; run timers instantly-ish.
jest.useFakeTimers();

beforeEach(async () => {
  const ctx = await createTestContext();
  mockServices = { ...ctx, feedback: noopFeedback };
});

async function typeInto(label: string, text: string) {
  fireEvent.changeText(await screen.findByLabelText(label), text);
}

describe('main user flow', () => {
  it('onboarding → habit → points → reward → archive → statistics → reopen', async () => {
    const app = renderRouter('./app', { initialUrl: '/' });

    // First launch: welcome for 3 s, then onboarding automatically.
    await screen.findByText('Привет!');
    act(() => jest.advanceTimersByTime(3000));

    // Goal step: create a goal.
    await screen.findByText('Твоя первая цель');
    await typeInto('Название', 'Кино');
    await typeInto('Стоимость в баллах', '15');
    fireEvent.press(screen.getByText('Создать'));

    // Wish step: skip.
    await screen.findByText('Твоё первое желание');
    fireEvent.press(screen.getByText('Пропустить'));

    // Habit step: create a habit for every day, 10 points, limit 2.
    await screen.findByText('Давай создадим\nтвою задачу!');
    expect(screen.getByLabelText('Шаг 3 из 3')).toBeTruthy();
    await typeInto('Название задачи', 'Зарядка');
    for (const day of ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']) {
      fireEvent.press(screen.getByLabelText(day));
    }
    await typeInto('Стоимость задачи', '10');
    await typeInto('Лимит выполнений в день', '2');
    fireEvent.press(screen.getByText('Продолжить'));

    // Tasks screen.
    await waitFor(() => expect(app.getPathname()).toBe('/tasks'));
    await screen.findByText('Зарядка');
    expect(screen.getByLabelText('Баланс: 0 баллов')).toBeTruthy();

    // Complete twice → limit reached.
    fireEvent.press(screen.getByLabelText('Выполнить: Зарядка'), { nativeEvent: { pageX: 0, pageY: 0 } });
    await screen.findByText('1/2');
    fireEvent.press(screen.getByLabelText('Выполнить: Зарядка'), { nativeEvent: { pageX: 0, pageY: 0 } });
    await screen.findByText('2/2');
    await screen.findByText('На сегодня выполнено');
    act(() => jest.advanceTimersByTime(4000)); // let the points land in the counter
    await screen.findByLabelText('Баланс: 20 баллов');

    // Rewards → goal → redeem.
    fireEvent.press(screen.getByLabelText('Награды'));
    await screen.findByText('Кино');
    expect(screen.getByText('Можно получить')).toBeTruthy();
    fireEvent.press(screen.getByLabelText('Кино'));
    await screen.findByText('Получить');
    fireEvent.press(screen.getByText('Получить'));
    await screen.findByText('Награда перенесена в архив.');

    // Archive shows it; balance debited.
    app.unmount();
    renderRouter('./app', { initialUrl: '/rewards' });
    await screen.findByLabelText('Баланс: 5 баллов');
    fireEvent.press(screen.getByText('Архив'));
    await screen.findByText('Кино');
    expect(screen.getByText(/Цель · получена/)).toBeTruthy();

    // Statistics.
    fireEvent.press(screen.getByLabelText('Статистика'));
    await screen.findByText('Выполнено сегодня');
    expect(screen.getByText('1 день')).toBeTruthy(); // streak

    // Reopen: onboarding is not shown again, data persisted.
    screen.unmount();
    const reopened = renderRouter('./app', { initialUrl: '/' });
    await screen.findByText('Привет!'); // welcome on every cold start
    act(() => jest.advanceTimersByTime(3000));
    await screen.findByText('Зарядка');
    expect(reopened.getPathname()).toBe('/tasks');
    expect(screen.getByLabelText('Баланс: 5 баллов')).toBeTruthy();
  });

  it('cancels today’s completion from the habit screen', async () => {
    const habit = await createHabit(mockServices, {
      name: 'Вода',
      weekdays: [0, 1, 2, 3, 4, 5, 6],
      pointsPerCompletion: 3,
      dailyLimit: 1,
    });
    await settingsRepository.setOnboardingCompleted(mockServices.db);
    await completeHabit(mockServices, habit.id);

    renderRouter('./app', { initialUrl: `/habit/${habit.id}` });
    await screen.findByText('Выполнено 1 из 1');
    fireEvent.press(screen.getByText('Отменить'));
    await screen.findByText('Выполнено 0 из 1');
  });

  it('replays the welcome from Профиль without touching data', async () => {
    const habit = await createHabit(mockServices, {
      name: 'Чтение',
      weekdays: [0, 1, 2, 3, 4, 5, 6],
      pointsPerCompletion: 4,
      dailyLimit: 1,
    });
    await settingsRepository.setOnboardingCompleted(mockServices.db);
    await completeHabit(mockServices, habit.id);
    const before = await mockServices.db.getAllAsync('SELECT * FROM point_transactions');

    const app = renderRouter('./app', { initialUrl: '/profile' });
    fireEvent.press(await screen.findByText('Посмотреть приветствие'));
    await screen.findByText('Привет!');
    expect(app.getPathname()).toBe('/welcome');

    fireEvent.press(screen.getByText('Начать'));
    await waitFor(() => expect(app.getPathname()).toBe('/profile'));

    expect(await settingsRepository.isOnboardingCompleted(mockServices.db)).toBe(true);
    expect(await mockServices.db.getAllAsync('SELECT * FROM point_transactions')).toEqual(before);
    expect(await mockServices.db.getAllAsync('SELECT * FROM habits WHERE deleted_at IS NULL')).toHaveLength(1);
  });

  it('creates a task from «Задачи» with the task creation screen', async () => {
    await settingsRepository.setOnboardingCompleted(mockServices.db);
    const app = renderRouter('./app', { initialUrl: '/tasks' });
    fireEvent.press(await screen.findByText('Добавить привычку'));
    await screen.findByText('Новая задача');
    expect(screen.queryByLabelText(/^Шаг /)).toBeNull(); // no onboarding step outside onboarding
    expect(screen.getByLabelText('Лимит выполнений в день').props.value).toBe('1'); // default limit

    // Empty form: nothing is saved, errors are shown.
    fireEvent.press(screen.getByText('Продолжить'));
    await screen.findByText('Введи название задачи');
    expect(screen.getByText('Укажи целое число баллов, минимум 1')).toBeTruthy();
    expect(screen.getByText('Выбери хотя бы один день')).toBeTruthy();

    // Name: counter and 60-char limit; points: digits only, zero rejected.
    await typeInto('Название задачи', 'Читать книгу');
    expect(screen.getByText('12/60')).toBeTruthy();
    expect(screen.getByLabelText('Название задачи').props.maxLength).toBe(60);
    await typeInto('Стоимость задачи', '0');
    fireEvent.press(screen.getByLabelText('Среда'));
    fireEvent.press(screen.getByText('Продолжить'));
    await screen.findByText('Укажи целое число баллов, минимум 1');
    expect(await mockServices.db.getAllAsync('SELECT * FROM habits')).toHaveLength(0);

    await typeInto('Стоимость задачи', '-2.5');
    expect(screen.getByLabelText('Стоимость задачи').props.value).toBe('25');
    expect(screen.getByLabelText('Стоимость задачи').props.keyboardType).toBe('number-pad');

    fireEvent.press(screen.getByText('Продолжить'));
    await waitFor(() => expect(app.getPathname()).toBe('/tasks'));
    await screen.findByText('Читать книгу');
    const [habit] = await mockServices.db.getAllAsync<{ points_per_completion: number; daily_limit: number; selected_weekdays: number }>(
      'SELECT * FROM habits',
    );
    expect(habit).toMatchObject({ points_per_completion: 25, daily_limit: 1, selected_weekdays: 0b100 });
  });

  it('keeps the onboarding task step skippable', async () => {
    const app = renderRouter('./app', { initialUrl: '/onboarding/habit' });
    await screen.findByText('Давай создадим\nтвою задачу!');
    fireEvent.press(screen.getByText('Пропустить'));
    await waitFor(() => expect(app.getPathname()).toBe('/tasks'));
    expect(await settingsRepository.isOnboardingCompleted(mockServices.db)).toBe(true);
    expect(await mockServices.db.getAllAsync('SELECT * FROM habits')).toHaveLength(0);
  });

  it.each([
    ['/tasks', true],
    ['/rewards', true],
    ['/statistics', true],
    ['/habit/new', true],
    ['/reward/new?type=goal', true],
    ['/reward/new?type=wish', true],
    ['/onboarding/goal', true],
    ['/onboarding/wish', true],
  ])('%s uses the shared room; TOBI only when its render exists', async (url, hasRender) => {
    await settingsRepository.setOnboardingCompleted(mockServices.db);
    renderRouter('./app', { initialUrl: url });
    const room = await screen.findByTestId('room-background');
    expect(room.props.source).toBe(TOBI_ROOM_SHARED);
    expect(screen.queryAllByTestId('room-character')).toHaveLength(hasRender ? 1 : 0);
    expect(screen.queryByText(/^tobi_/)).toBeNull(); // no placeholder squares
  });
});

describe('cold start: welcome for 3 s, then onboarding or «Задачи»', () => {
  const { router } = jest.requireActual('expo-router') as typeof import('expo-router');
  const { startupDestination, WELCOME_SPLASH_MS } = jest.requireActual(
    '@/features/onboarding/startup',
  ) as typeof import('@/features/onboarding/startup');

  afterEach(() => jest.restoreAllMocks());

  it('maps the persisted flag to the destination', () => {
    expect(WELCOME_SPLASH_MS).toBe(3000);
    expect(startupDestination(false)).toBe('/onboarding/goal');
    expect(startupDestination(true)).toBe('/tasks');
  });

  it('new user: welcome without «Начать» for 3 s, then the goal step (no way back to the welcome)', async () => {
    const replace = jest.spyOn(router, 'replace');
    const app = renderRouter('./app', { initialUrl: '/' });
    await screen.findByText('Привет!');
    expect(screen.getByText('Я ТОБИ — твой напарник\nв больших и маленьких\nдостижениях.')).toBeTruthy();
    expect(screen.queryByRole('button', { name: 'Начать' })).toBeNull(); // hidden: no tap needed to continue

    act(() => jest.advanceTimersByTime(2999));
    expect(app.getPathname()).toBe('/');
    act(() => jest.advanceTimersByTime(1));
    await screen.findByText('Твоя первая цель');
    expect(app.getPathname()).toBe('/onboarding/goal');
    expect(replace).toHaveBeenCalledTimes(1);
    expect(router.canGoBack()).toBe(false);
    expect(screen.queryByLabelText('Назад')).toBeNull(); // first step: nothing to go back to
  });

  it('existing user: welcome, then «Задачи» with the data kept', async () => {
    await settingsRepository.setOnboardingCompleted(mockServices.db);
    await createHabit(mockServices, { name: 'Вода', weekdays: [0, 1, 2, 3, 4, 5, 6], pointsPerCompletion: 3, dailyLimit: 1 });
    const app = renderRouter('./app', { initialUrl: '/' });
    await screen.findByText('Привет!');
    act(() => jest.advanceTimersByTime(3000));
    await screen.findByText('Вода');
    expect(app.getPathname()).toBe('/tasks');
    expect(screen.queryByText('Твоя первая цель')).toBeNull();
  });

  it('existing user who deleted all habits does not get onboarding again', async () => {
    await settingsRepository.setOnboardingCompleted(mockServices.db);
    const app = renderRouter('./app', { initialUrl: '/' });
    act(() => jest.advanceTimersByTime(3000));
    await screen.findByText('Добавить привычку');
    expect(app.getPathname()).toBe('/tasks');
  });

  it('skipping every optional step still completes onboarding', async () => {
    const app = renderRouter('./app', { initialUrl: '/' });
    act(() => jest.advanceTimersByTime(3000));
    await screen.findByText('Твоя первая цель');
    fireEvent.press(screen.getByText('Пропустить'));
    await screen.findByText('Твоё первое желание');
    fireEvent.press(screen.getByText('Пропустить'));
    await screen.findByText('Давай создадим\nтвою задачу!');
    fireEvent.press(screen.getByText('Пропустить'));
    await waitFor(() => expect(app.getPathname()).toBe('/tasks'));
    expect(await settingsRepository.isOnboardingCompleted(mockServices.db)).toBe(true);
  });

  it('slow storage: waits for the state after 3 s instead of guessing', async () => {
    await settingsRepository.setOnboardingCompleted(mockServices.db);
    let resolve!: (v: boolean) => void;
    jest.spyOn(settingsRepository, 'isOnboardingCompleted').mockReturnValue(new Promise((r) => (resolve = r)));
    const replace = jest.spyOn(router, 'replace');
    const app = renderRouter('./app', { initialUrl: '/' });
    await screen.findByText('Привет!');
    act(() => jest.advanceTimersByTime(5000));
    expect(app.getPathname()).toBe('/');
    expect(replace).not.toHaveBeenCalled();
    await act(async () => resolve(true));
    await waitFor(() => expect(app.getPathname()).toBe('/tasks'));
    expect(replace).toHaveBeenCalledTimes(1);
  });

  it('closing during the welcome: no navigation and no errors after unmount', async () => {
    const replace = jest.spyOn(router, 'replace');
    const errors = jest.spyOn(console, 'error');
    const app = renderRouter('./app', { initialUrl: '/' });
    await screen.findByText('Привет!');
    act(() => jest.advanceTimersByTime(1000));
    app.unmount();
    act(() => jest.advanceTimersByTime(5000));
    expect(replace).not.toHaveBeenCalled();
    expect(errors).not.toHaveBeenCalled();
  });

  it('switching tabs never shows the welcome again', async () => {
    await settingsRepository.setOnboardingCompleted(mockServices.db);
    renderRouter('./app', { initialUrl: '/' });
    act(() => jest.advanceTimersByTime(3000));
    await screen.findByText('Привычки');
    const tabs: [string, string][] = [
      ['Награды', 'Пока нет целей'],
      ['Статистика', 'Эта неделя'],
      ['Профиль', 'Посмотреть приветствие'],
      ['Задачи', 'Добавить привычку'],
    ];
    for (const [tab, content] of tabs) {
      fireEvent.press(screen.getByLabelText(tab));
      await screen.findByText(content);
      act(() => jest.advanceTimersByTime(3000));
      expect(screen.queryByText(/Я ТОБИ — твой напарник/)).toBeNull();
    }
  });
});

describe('editing a goal or wish', () => {
  it.each([
    ['goal', 'Кино', 50],
    ['wish', 'Кофе', 10],
  ] as const)('edits an existing %s in place with TOBI and the notebook in the room', async (type, name, cost) => {
    await settingsRepository.setOnboardingCompleted(mockServices.db);
    const reward = await createReward(mockServices, type, { name, cost });
    const app = renderRouter('./app', { initialUrl: `/reward/${reward.id}` });
    await screen.findByText(name);
    fireEvent.press(screen.getByText('Редактировать'));

    await screen.findByText('Редактировать награду');
    const room = screen.getByTestId('room-background');
    expect(room.props.source).toBe(TOBI_ROOM_SHARED);
    expect(screen.getAllByTestId('room-character')).toHaveLength(1);
    expect(screen.getByLabelText('Название').props.value).toBe(name); // current data shown
    expect(screen.getByLabelText('Стоимость в баллах').props.value).toBe(String(cost));

    await typeInto('Название', `${name} с друзьями`);
    await typeInto('Стоимость в баллах', String(cost * 2));
    fireEvent.press(screen.getByText('Сохранить'));
    await screen.findByText(`${name} с друзьями`); // back on the reward screen with the new name
    expect(app.getPathname()).toBe(`/reward/${reward.id}`);
    expect(await getReward(mockServices, reward.id)).toMatchObject({ name: `${name} с друзьями`, cost: cost * 2, type, status: 'active' });
    expect(await mockServices.db.getAllAsync('SELECT * FROM rewards')).toHaveLength(1); // updated, not duplicated

    // Reopen: saved values are shown.
    app.unmount();
    renderRouter('./app', { initialUrl: `/reward/${reward.id}` });
    await screen.findByText(`${name} с друзьями`);
    fireEvent.press(screen.getByText('Редактировать'));
    await screen.findByText('Редактировать награду');
    expect(screen.getByLabelText('Название').props.value).toBe(`${name} с друзьями`);
    expect(screen.getByLabelText('Стоимость в баллах').props.value).toBe(String(cost * 2));
  });

  it('leaving with «Назад» does not save changes', async () => {
    await settingsRepository.setOnboardingCompleted(mockServices.db);
    const reward = await createReward(mockServices, 'goal', { name: 'Кино', cost: 50 });
    renderRouter('./app', { initialUrl: `/reward/${reward.id}` });
    await screen.findByText('Кино');
    fireEvent.press(screen.getByText('Редактировать'));
    await screen.findByText('Редактировать награду');
    await typeInto('Название', 'Другое');
    fireEvent.press(screen.getByLabelText('Назад'));
    await waitFor(() => expect(screen.queryByText('Редактировать награду')).toBeNull());
    expect(await getReward(mockServices, reward.id)).toMatchObject({ name: 'Кино', cost: 50 });
  });
});


describe('item icons', () => {
  const pickIcon = async (current: RegExp, label: string) => {
    fireEvent.press(await screen.findByLabelText(current));
    await screen.findByText('Выбрать иконку');
    fireEvent.press(screen.getByLabelText(label));
    fireEvent.press(screen.getByText('Выбрать'));
  };

  it('task: choose an icon on creation, see it in «Задачи», change it on edit; ✕ keeps the old one', async () => {
    await settingsRepository.setOnboardingCompleted(mockServices.db);
    const app = renderRouter('./app', { initialUrl: '/tasks' });
    fireEvent.press(await screen.findByText('Добавить привычку'));
    await screen.findByText('Новая задача');
    expect(screen.getByTestId('tobi-icon-default_habit')).toBeTruthy(); // default before choosing

    await pickIcon(/^Иконка: .*\. Изменить$/, 'Спорт');
    await screen.findByTestId('tobi-icon-sport');
    await typeInto('Название задачи', 'Бег');
    await typeInto('Стоимость задачи', '10');
    fireEvent.press(screen.getByLabelText('Понедельник'));
    fireEvent.press(screen.getByText('Продолжить'));
    await waitFor(() => expect(app.getPathname()).toBe('/tasks'));
    await screen.findByText('Бег');
    expect(screen.getByTestId('tobi-icon-sport')).toBeTruthy(); // shown in the task card

    const [row] = await mockServices.db.getAllAsync<{ id: string; icon_id: string }>('SELECT id, icon_id FROM habits');
    expect(row!.icon_id).toBe('sport');

    // Edit: previous icon shown, change to water.
    app.unmount();
    const edit = renderRouter('./app', { initialUrl: `/habit/${row!.id}` });
    await screen.findByText('Бег');
    fireEvent.press(screen.getByText('Редактировать'));
    await screen.findByLabelText('Иконка: Спорт. Изменить');
    // Close the picker with ✕: nothing changes.
    fireEvent.press(screen.getByLabelText('Иконка: Спорт. Изменить'));
    await screen.findByText('Выбрать иконку');
    fireEvent.press(screen.getByLabelText('Вода'));
    fireEvent.press(screen.getByLabelText('Отмена'));
    expect(screen.getByLabelText('Иконка: Спорт. Изменить')).toBeTruthy();
    await pickIcon(/^Иконка: Спорт\. Изменить$/, 'Вода');
    await screen.findByLabelText('Иконка: Вода. Изменить');
    fireEvent.press(screen.getByText('Сохранить'));
    await waitFor(() => expect(edit.getPathname()).toBe(`/habit/${row!.id}`));
    await screen.findByTestId('tobi-icon-water');
    const [after] = await mockServices.db.getAllAsync<{ icon_id: string }>('SELECT icon_id FROM habits');
    expect(after!.icon_id).toBe('water');
  });

  it('goal and wish: chosen icons are shown in «Награды»; leaving edit without saving keeps the icon', async () => {
    await settingsRepository.setOnboardingCompleted(mockServices.db);
    renderRouter('./app', { initialUrl: '/rewards' });
    fireEvent.press(await screen.findByText('Добавить цель'));
    await screen.findByText('Новая цель');
    await typeInto('Название', 'Прочитать 12 книг');
    await typeInto('Стоимость в баллах', '120');
    await pickIcon(/^Иконка: Цель\. Изменить$/, 'Чтение');
    await screen.findByLabelText('Иконка: Чтение. Изменить');
    fireEvent.press(screen.getByText('Создать цель'));
    await screen.findByText('Прочитать 12 книг');

    fireEvent.press(screen.getByText('Желания'));
    fireEvent.press(await screen.findByText('Добавить желание'));
    await screen.findByText('Новое желание');
    await typeInto('Название', 'Путешествие'); // no icon chosen → default wish icon
    await typeInto('Стоимость в баллах', '5000');
    fireEvent.press(screen.getByText('Создать желание'));
    await screen.findByText('Путешествие');

    fireEvent.press(screen.getByText('Цели'));
    await screen.findByText('Прочитать 12 книг');
    expect(screen.getByTestId('tobi-icon-reading')).toBeTruthy();
    fireEvent.press(screen.getByText('Желания'));
    await screen.findByText('Путешествие');
    expect(screen.getByTestId('tobi-icon-default_wish')).toBeTruthy();

    // Edit the wish icon but leave with «Назад»: nothing saved.
    fireEvent.press(screen.getByLabelText('Путешествие'));
    fireEvent.press(await screen.findByText('Редактировать'));
    await pickIcon(/^Иконка: Желание\. Изменить$/, 'Сон');
    fireEvent.press(screen.getByLabelText('Назад'));
    await waitFor(() => expect(screen.queryByText('Редактировать награду')).toBeNull());
    const rows = await mockServices.db.getAllAsync<{ name: string; icon_id: string }>('SELECT name, icon_id FROM rewards ORDER BY name');
    expect(rows).toEqual([
      { name: 'Прочитать 12 книг', icon_id: 'reading' },
      { name: 'Путешествие', icon_id: 'default_wish' },
    ]);
  });

  it('the last library icon can be chosen; previously saved temporary ids show the new images', async () => {
    await settingsRepository.setOnboardingCompleted(mockServices.db);
    const old = await createReward(mockServices, 'wish', { name: 'Книга', cost: 30, iconId: 'reading' });
    renderRouter('./app', { initialUrl: '/rewards' });
    fireEvent.press(await screen.findByText('Желания'));
    await screen.findByText('Книга');
    expect(screen.getByTestId('tobi-icon-reading')).toBeTruthy();

    fireEvent.press(screen.getByLabelText('Книга'));
    fireEvent.press(await screen.findByText('Редактировать'));
    await pickIcon(/^Иконка: Чтение\. Изменить$/, 'Праздник');
    await screen.findByLabelText('Иконка: Праздник. Изменить');
    fireEvent.press(screen.getByText('Сохранить'));
    await waitFor(async () => expect((await getReward(mockServices, old.id))?.iconId).toBe('celebration'));
  });

  it('old records without an icon and unknown icon ids show the default icon without errors', async () => {
    await settingsRepository.setOnboardingCompleted(mockServices.db);
    const a = await createHabit(mockServices, { name: 'Старая', weekdays: [0, 1, 2, 3, 4, 5, 6], pointsPerCompletion: 1, dailyLimit: 1 });
    const b = await createHabit(mockServices, { name: 'Пропавшая', weekdays: [0, 1, 2, 3, 4, 5, 6], pointsPerCompletion: 1, dailyLimit: 1 });
    await mockServices.db.runAsync('UPDATE habits SET icon_id = NULL WHERE id = ?', [a.id]);
    await mockServices.db.runAsync("UPDATE habits SET icon_id = 'removed-icon' WHERE id = ?", [b.id]);
    renderRouter('./app', { initialUrl: '/tasks' });
    await screen.findByText('Старая');
    await screen.findByText('Пропавшая');
    expect(screen.getAllByTestId('tobi-icon-default_habit')).toHaveLength(2);
  });
});

describe('«Добавить …» cards after the lists', () => {
  it('Задачи: one card after the last habit (also when empty), opens the habit form', async () => {
    await settingsRepository.setOnboardingCompleted(mockServices.db);
    const app = renderRouter('./app', { initialUrl: '/tasks' });
    await screen.findByText('Пока нет привычек');
    expect(screen.getAllByText('Добавить привычку')).toHaveLength(1); // empty list: card still there
    expect(screen.queryByLabelText('Создать привычку')).toBeNull(); // no duplicate «+» in the header
    fireEvent.press(screen.getByText('Добавить привычку'));
    await screen.findByText('Новая задача');
    expect(app.getPathname()).toBe('/habit/new');
  });

  it('places the card after the last habit card', async () => {
    await settingsRepository.setOnboardingCompleted(mockServices.db);
    for (const name of ['Бег', 'Чтение', 'Вода']) {
      await createHabit(mockServices, { name, weekdays: [0, 1, 2, 3, 4, 5, 6], pointsPerCompletion: 1, dailyLimit: 1 });
    }
    renderRouter('./app', { initialUrl: '/tasks' });
    await screen.findByText('Вода');
    const texts = screen.UNSAFE_root.findAll((n) => typeof n.props.children === 'string' && String(n.type) === 'Text').map(
      (n) => n.props.children as string,
    );
    expect(texts.indexOf('Добавить привычку')).toBeGreaterThan(texts.indexOf('Вода'));
    expect(texts.filter((t) => t === 'Добавить привычку')).toHaveLength(1);
  });

  it('Цели and Желания: card opens the right form; no card in the archive', async () => {
    await settingsRepository.setOnboardingCompleted(mockServices.db);
    await createReward(mockServices, 'goal', { name: 'Кино', cost: 50 });
    const app = renderRouter('./app', { initialUrl: '/rewards' });
    await screen.findByText('Кино');
    expect(screen.getAllByText('Добавить цель')).toHaveLength(1);
    fireEvent.press(screen.getByText('Добавить цель'));
    await screen.findByText('Новая цель');
    expect(app.getSearchParams()).toMatchObject({ type: 'goal' });
    fireEvent.press(screen.getByLabelText('Назад'));

    fireEvent.press(await screen.findByText('Желания'));
    await screen.findByText('Пока нет желаний');
    fireEvent.press(screen.getByText('Добавить желание'));
    await screen.findByText('Новое желание');
    expect(app.getSearchParams()).toMatchObject({ type: 'wish' });
    fireEvent.press(screen.getByLabelText('Назад'));

    fireEvent.press(await screen.findByText('Архив'));
    await screen.findByText('Архив пуст');
    expect(screen.queryByText(/^Добавить /)).toBeNull();
  });
});

