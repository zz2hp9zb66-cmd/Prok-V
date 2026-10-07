# TOBI Habit — правила для Claude Code

**Источник истины:** `docs/TOBI_Habit_Master_Specification.md`. Перед любой задачей сверяйся с ним.

- Не добавлять функции, не менять бизнес-логику, не расширять MVP, не редизайнить TOBI (§1, §33).
- Если критичное поведение не описано в спецификации — спросить владельца продукта, а не придумывать.
- Решения владельца (`docs/decisions.md`) — часть спецификации. Новые решения записывать туда же.
- Прогресс по §34 — `docs/progress.md`.

## Стек
Expo SDK 57 · React Native · TypeScript (strict) · Expo Router · expo-sqlite. Offline-first, без сервера и аккаунтов.

Expo часто ломает API между SDK: перед использованием API Expo/RN сверяйся с документацией
`https://docs.expo.dev/versions/v57.0.0/` или с типами в `node_modules`.

## Команды
```bash
npm start              # dev server
npm test               # Jest (нужен Node >= 22.13: тесты используют node:sqlite)
npm run typecheck      # tsc для приложения и тестов
npx expo install <pkg> # добавлять зависимости только так (в этой среде: EXPO_OFFLINE=1)
npx expo start --web   # только превью в браузере; web не целевая платформа
```
Перед завершением задачи: `npm run typecheck && npm test`.

## Архитектура
```
app/          маршруты Expo Router (тонкие обёртки, без логики)
components/   компоненты Design System (§23)
features/     экраны и доменная логика по фичам (onboarding, habits, rewards, points, statistics, profile, tobi)
data/db/      SqlDatabase-интерфейс, адаптер expo-sqlite, миграции (PRAGMA user_version)
data/repositories/  доступ к таблицам
data/ServicesContext.tsx  DI: db, clock, ids, feedback (useServices); DataProvider подключает expo-sqlite
services/     time (единый сервис времени), ids, feedback (звук/haptic — заглушка до тестовой версии)
theme/        токены Design System (§22)
tests/        Jest: доменные тесты на in-memory node:sqlite; appFlow.test.tsx — UI-сценарий через
              expo-router/testing-library с подменой DataProvider
```

## Инварианты
- Баланс = сумма `point_transactions`. Менять баланс только через сервис баллов, никогда напрямую из экранов (§26).
- Баланс никогда не отрицательный; связанные изменения — в одной транзакции `db.transaction(...)`.
- Сначала сохраняется бизнес-событие, потом анимация/звук/haptic (§29).
- Дневная логика — только через `services/time` (локальная дата, новый день в 00:00) (§8, §27).
- Прошлые выполнения не пересчитываются; удаление привычки — soft delete, история остаётся (§11).
- Изменения баллов/лимита привычки — через pending-поля, со следующего дня; имя и дни — сразу (D3).
- Отмена выполнения — только сегодняшнего и только если баланс останется ≥ 0 (D1).
- Экраны не пишут в БД напрямую — только через сервисы в `features/*/…Service.ts`.
- UI только на русском (D6), обращение на «ты».
- Миграции не редактировать после релиза — только добавлять новые.
- В экранах не хардкодить цвета/отступы/радиусы/шрифты — брать из `theme/`.
- TOBI — только готовые ассеты из `assets/tobi/` (реестр `features/tobi/tobiAssets.ts`).
