import { act, fireEvent, renderRouter, screen, waitFor } from 'expo-router/testing-library';
import { settingsRepository } from '@/data/repositories/settingsRepository';
import type { AppServices } from '@/data/ServicesContext';
import { completeHabit, createHabit } from '@/features/habits/habitsService';
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

    // First launch: onboarding.
    await screen.findByText('Привет!');
    fireEvent.press(screen.getByText('Начать'));

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
    fireEvent.press(await screen.findByText('Создать первую привычку'));
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
    ['/statistics', false],
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
