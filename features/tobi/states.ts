/**
 * TOBI states — spec §19–20.
 * TOBI is shown via pre-rendered 3D images and pre-made animation files.
 * Claude Code does not create or redesign TOBI: assets are supplied by the
 * product owner into `assets/tobi/` and registered in `tobiAssets.ts`.
 */
export const TOBI_STATES = [
  'tobi_idle', // обычное — улыбается (анимация желательна)
  'tobi_wave', // приветствие — машет (анимация обязательна)
  'tobi_habit_complete', // выполнение привычки — радуется, большой палец (обязательна)
  'tobi_reward', // получение награды — очень радуется (обязательна)
  'tobi_goal_create', // создание цели — карандаш (статично)
  'tobi_wish_create', // создание желания — мечтает (статично)
  'tobi_habit_create', // создание привычки — список (статично)
  'tobi_statistics', // статистика — показывает вверх (анимация желательна)
  'tobi_tasks', // шапка раздела «Задачи» (статично)
  'tobi_rewards', // шапка раздела «Награды» (статично)
] as const;

export type TobiState = (typeof TOBI_STATES)[number];
