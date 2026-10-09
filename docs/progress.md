# Прогресс MVP (§34)

| # | Этап | Статус |
|---|------|--------|
| 1 | Expo / React Native / TypeScript | ✅ |
| 2 | Навигация | ✅ Expo Router: onboarding-gate, 4 вкладки, стек экранов привычек/наград |
| 3 | Design System tokens | ✅ `theme/` |
| 4 | SQLite + migrations | ✅ `data/db/migrations.ts` (v1) |
| 5 | Data/repository layer | ✅ `data/repositories/` |
| 6 | Point transaction logic | ✅ `features/points/pointsService.ts` |
| 7 | Habits domain | ✅ `features/habits/habitsService.ts` |
| 8 | Rewards domain | ✅ `features/rewards/rewardsService.ts` |
| 9 | Onboarding | ✅ |
| 10 | Tasks screen | ✅ |
| 11 | Rewards + archive | ✅ |
| 12 | Statistics | ✅ |
| 13 | Profile/settings | ✅ (D5) |
| 14 | TOBI assets | 🟡 подключены `tobi_wave`, `tobi_habit_create`, `tobi_goal_create`; остальные ждут рендеры |
| 15 | TOBI/UI animations | 🟡 UI-анимация «+N → счётчик» и переключение состояний TOBI готовы; анимации самого TOBI — после ассетов и выбора формата (§20) |
| 16 | Tests | ✅ домен (§30) + сквозной UI-сценарий DoD (§35) |
| 17 | Offline verification | ✅ в коде нет сетевых вызовов; все данные в локальной SQLite |
| 18 | Test build on iPhone / Android | ⏳ нужен аккаунт Expo/EAS и устройства владельца |
| 19 | Sound design / haptic | ⏳ после тестовой версии; точка подключения — `services/feedback.ts` |

## Как подключить TOBI-ассеты
1. Положить рендеры в `assets/tobi/` (`tobi_idle.png`, `tobi_wave.png`, …).
2. Зарегистрировать в `features/tobi/tobiAssets.ts`: `tobi_idle: require('@/assets/tobi/tobi_idle.png')`.
3. Placeholder исчезнет автоматически для зарегистрированных состояний.

## Фон приветственного экрана
- Экран: `features/onboarding/WelcomeScreen.tsx`, слои: комната → прозрачный слой TOBI → текст и «Начать».
- Фон подключён: `assets/tobi/welcome_room.webp` — оригинальный файл владельца без изменений (WebP 853×1844),
  зарегистрирован в `features/tobi/tobiAssets.ts` (`tobiScenes.welcomeRoom`).
- Слой TOBI (`tobi_wave`) заканчивается на 64% высоты экрана — на линии пола комнаты (≈62% изображения 853×1844).

## Экран «Создание задачи»
- `features/habits/HabitCreateScreen.tsx` — общий для онбординга (`/onboarding/habit`) и обычного создания (`/habit/new`).
- Ожидают ассеты: TOBI с блокнотом/карандашом (`tobi_habit_create`, слот `task-create-tobi-layer`),
  отдельная сцена комнаты для этого экрана (`tobiScenes.taskCreateRoom`, сейчас = `welcome_room.webp`),
  облачко-«мысль» с иконкой из макета — часть будущего рендера TOBI.

## TOBI-рендеры
- ✅ `tobi_wave` — `assets/tobi/tobi_wave.webp` (оригинал владельца, WebP с прозрачностью, 1024×1536), приветственный экран.
- ✅ `tobi_habit_create` — `assets/tobi/tobi_habit_create.png` (PNG с прозрачностью, 1554×1012, пиксели идентичны присланному файлу), экран «Создание задачи».
- ✅ `tobi_goal_create` — `assets/tobi/tobi_goal_create.webp` (оригинал владельца, WebP с прозрачностью, 1426×1103), шаг онбординга «цель» и «Новая цель».
- ⏳ Ждут прозрачных PNG/WebP: `tobi_wish_create`, `tobi_idle`,
  `tobi_habit_complete`, `tobi_reward`, `tobi_statistics`.

## Единая комната (D13)
- Фон: `assets/backgrounds/tobi_room_shared.webp`, подключён один раз в `TOBI_ROOM_SHARED` (`features/tobi/tobiAssets.ts`).
- Шапка: `components/TOBIRoomHeader.tsx`; экраны: `components/RoomScreen.tsx`.
- Подключение персонажей — см. `assets/tobi/README.md`.
