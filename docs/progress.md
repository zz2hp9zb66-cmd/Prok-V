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
| 14 | TOBI assets | ⏳ ждём ассеты от владельца; сейчас нейтральные placeholders |
| 15 | TOBI/UI animations | 🟡 UI-анимация «+N → счётчик» и переключение состояний TOBI готовы; анимации самого TOBI — после ассетов и выбора формата (§20) |
| 16 | Tests | ✅ домен (§30) + сквозной UI-сценарий DoD (§35) |
| 17 | Offline verification | ✅ в коде нет сетевых вызовов; все данные в локальной SQLite |
| 18 | Test build on iPhone / Android | ⏳ нужен аккаунт Expo/EAS и устройства владельца |
| 19 | Sound design / haptic | ⏳ после тестовой версии; точка подключения — `services/feedback.ts` |

## Как подключить TOBI-ассеты
1. Положить рендеры в `assets/tobi/` (`tobi_idle.png`, `tobi_wave.png`, …).
2. Зарегистрировать в `features/tobi/tobiAssets.ts`: `tobi_idle: require('@/assets/tobi/tobi_idle.png')`.
3. Placeholder исчезнет автоматически для зарегистрированных состояний.
