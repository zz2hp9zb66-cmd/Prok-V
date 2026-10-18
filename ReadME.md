# Collage B-Roll

Локальная система автоматического производства анимированных видеоколлажей (Editorial Collage / Paper Cutout) по текстовому сценарию.

- [Технический анализ, архитектура и план MVP](docs/ARCHITECTURE.md)

## Состав

- `cbroll/` — конвейер на Python: разбор сценария, ассеты, вырезка фона (rembg + BiRefNet), композиция, анимация, рендер.
- `renderer/` — Remotion (React/TypeScript): коллаж, пресеты движения, камера с параллаксом, переходы.
- `projects/<name>/` — всё состояние проекта: `script.md`, `project.json`, `timeline.json`, `scenes/*/scene.json`, `assets/` (оригиналы, маски, вырезки, стилизованные версии, метаданные лицензий), `previews/`, `output/`.

## Установка (macOS)

```bash
scripts/check_mac.sh                 # проверка оборудования и инструментов
uv venv && uv pip install -e .
(cd renderer && npm ci)
```

## Конвейер

```bash
P=projects/blue-note-test
cbroll analyze $P                    # script.md -> сцены + длительности по темпу
cbroll apply-plan $P $P/plan.json    # визуальный план сцен (готовит Claude Code)
cbroll test-assets $P                # офлайн-заглушки, если фотоархивы недоступны
cbroll cutout $P                     # удаление фона + стиль «бумажной вырезки»
cbroll compose $P [-s 02] [--reseed] # раскладка слоёв
cbroll preview $P                    # previews/storyboard.png + storyboard.html
cbroll approve $P all                # обязательное утверждение
cbroll animate $P                    # анимация, камера, переходы (только после утверждения)
cbroll render $P                     # output/final.mp4, 1080×1920, 30 fps, без звука
cbroll set-duration $P 02 7.5        # изменить длительность сцены без пересборки композиции
```
