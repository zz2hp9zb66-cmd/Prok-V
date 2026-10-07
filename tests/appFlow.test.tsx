import { act, fireEvent, renderRouter, screen, waitFor } from 'expo-router/testing-library';
import { settingsRepository } from '@/data/repositories/settingsRepository';
import type { AppServices } from '@/data/ServicesContext';
import { completeHabit, createHabit } from '@/features/habits/habitsService';
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
    await screen.findByText('Привет, я TOBI!');
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
    await screen.findByText('Твоя первая привычка');
    await typeInto('Название', 'Зарядка');
    for (const day of ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']) {
      fireEvent.press(screen.getByLabelText(day));
    }
    await typeInto('Баллы за выполнение', '10');
    await typeInto('Лимит выполнений в день', '2');
    fireEvent.press(screen.getByText('Создать'));

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
});
