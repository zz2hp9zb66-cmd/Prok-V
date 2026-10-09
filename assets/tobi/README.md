# TOBI assets

Static TOBI renders (transparent PNG/WebP, no frame or background) supplied by the product owner.
TOBI is never generated or redesigned in code (§20, §33).

## How to connect a render
1. Put the file here, e.g. `assets/tobi/tobi_tasks.png`.
2. Add one entry to `tobiRenders` in `features/tobi/tobiAssets.ts`:
   `tobi_reward: { source: require('@/assets/tobi/tobi_reward.png'), width: <px>, height: <px> }`.
3. The screen picks it up automatically. Until then the room headers show only the room.

| State | Screen |
|---|---|
| `tobi_wave` ✅ | Welcome |
| `tobi_habit_create` ✅ | Task creation |
| `tobi_goal_create` ✅ | Goal creation (onboarding + «Новая цель») |
| `tobi_wish_create` ✅ | Wish creation (onboarding + «Новое желание») |
| `tobi_tasks` ✅ | «Задачи» header |
| `tobi_rewards` ✅ | «Награды» header |
| `tobi_statistics` ✅ | «Статистика» header |
| `tobi_reward_edit` ✅ | Editing a goal or wish («Редактировать награду», taller `hero` header) |
| `tobi_habit_complete` | short reaction on «Задачи» after a completion |

Position/size can be set once per render with `placement: { scale, offsetX, offsetY }` in `tobiRenders`,
or per screen with `characterScale`, `characterOffsetX`, `characterOffsetY` on `RoomScreen` / `TOBIRoomHeader`.

Shared room for all these headers: `assets/backgrounds/tobi_room_shared.webp`.
The welcome screen keeps its own scene `assets/tobi/welcome_room.webp`.
