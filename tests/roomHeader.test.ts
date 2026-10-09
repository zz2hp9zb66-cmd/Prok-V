import { computeRoomCharacterFrame, ROOM_PANEL_OVERLAP, roomHeaderHeight } from '@/components/TOBIRoomHeader';
import { HABIT_CREATE_TOBI_SCALE, HABIT_CREATE_TOBI_VISIBLE } from '@/features/habits/habitCreateTobi';
import { tobiRenders } from '@/features/tobi/tobiAssets';

const DEVICES = {
  'iPhone SE': { width: 375, height: 667, top: 20 },
  'iPhone 13 mini': { width: 375, height: 812, top: 50 },
  'iPhone 15': { width: 393, height: 852, top: 59 },
  'iPhone 15 Pro Max': { width: 430, height: 932, top: 59 },
};

describe.each(Object.entries(DEVICES))('room header on %s', (_, d) => {
  it('scales the header with the screen and includes the status bar area', () => {
    for (const variant of ['form', 'section'] as const) {
      const h = roomHeaderHeight(variant, d.height, d.top);
      expect(h - d.top).toBeGreaterThanOrEqual(140);
      expect(h - d.top).toBeLessThanOrEqual(0.3 * d.height);
    }
    expect(roomHeaderHeight('form', d.height, d.top)).toBeGreaterThan(roomHeaderHeight('section', d.height, d.top));
  });

  it('places a generic render on the panel edge, under the status bar, within the width', () => {
    const headerHeight = roomHeaderHeight('section', d.height, d.top);
    const f = computeRoomCharacterFrame({ screenWidth: d.width, insetTop: d.top, headerHeight, aspect: 1.2 });
    expect(f.width / f.height).toBeCloseTo(1.2);
    expect(f.top).toBeGreaterThanOrEqual(d.top);
    expect(f.top + f.height).toBeCloseTo(headerHeight - ROOM_PANEL_OVERLAP);
    expect(f.left).toBeGreaterThanOrEqual(0);
    expect(f.left + f.width).toBeLessThanOrEqual(d.width);
  });

  it('shows tobi_habit_create with the head and notebook visible and the hem behind the panel', () => {
    const r = tobiRenders.tobi_habit_create!;
    const headerHeight = roomHeaderHeight('form', d.height, d.top);
    const panelTop = headerHeight - ROOM_PANEL_OVERLAP;
    const f = computeRoomCharacterFrame({
      screenWidth: d.width,
      insetTop: d.top,
      headerHeight,
      aspect: r.width / r.height,
      scale: HABIT_CREATE_TOBI_SCALE,
      offsetY: 1 - HABIT_CREATE_TOBI_VISIBLE,
    });
    expect(f.top).toBeGreaterThanOrEqual(d.top);
    expect(f.top + f.height * 0.94).toBeLessThanOrEqual(panelTop + 0.5);
    expect(f.top + f.height).toBeGreaterThan(panelTop);
    expect(f.left + f.width).toBeLessThanOrEqual(d.width);
    expect(f.width).toBeGreaterThan(d.width * 0.55);
  });

  it('applies offsets: X as a share of the screen width, Y as a share of the character height', () => {
    const base = { screenWidth: d.width, insetTop: d.top, headerHeight: roomHeaderHeight('form', d.height, d.top), aspect: 1 };
    const a = computeRoomCharacterFrame(base);
    const b = computeRoomCharacterFrame({ ...base, offsetX: 0.1, offsetY: 0.2 });
    expect(b.left - a.left).toBeCloseTo(0.1 * d.width);
    expect(b.top - a.top).toBeCloseTo(0.2 * a.height);
  });

  it('shows tobi_goal_create with the cloud, pencil and paws visible', () => {
    const r = tobiRenders.tobi_goal_create!;
    const headerHeight = roomHeaderHeight('form', d.height, d.top);
    const panelTop = headerHeight - ROOM_PANEL_OVERLAP;
    const f = computeRoomCharacterFrame({
      screenWidth: d.width,
      insetTop: d.top,
      headerHeight,
      aspect: r.width / r.height,
      scale: r.placement?.scale,
      offsetY: r.placement?.offsetY,
    });
    expect(f.width / f.height).toBeCloseTo(r.width / r.height);
    expect(f.top).toBeGreaterThanOrEqual(d.top); // thought cloud and ears under the status bar
    expect(f.top + f.height * 0.83).toBeLessThanOrEqual(panelTop + 0.5); // both paws above the panel
    expect(f.left).toBeGreaterThanOrEqual(0);
    expect(f.left + f.width).toBeLessThanOrEqual(d.width);
    expect(f.width).toBeGreaterThan(d.width * 0.5);
    // Back button (16..60 px) only meets the transparent left edge of the render (tail starts below 55%).
    expect(f.left + f.width * 0.25).toBeGreaterThan(60);
  });

  it('shows tobi_wish_create with all thought clouds and paws visible', () => {
    const r = tobiRenders.tobi_wish_create!;
    const headerHeight = roomHeaderHeight('form', d.height, d.top);
    const panelTop = headerHeight - ROOM_PANEL_OVERLAP;
    const f = computeRoomCharacterFrame({
      screenWidth: d.width,
      insetTop: d.top,
      headerHeight,
      aspect: r.width / r.height,
      scale: r.placement?.scale,
      offsetY: r.placement?.offsetY,
    });
    expect(f.width / f.height).toBeCloseTo(r.width / r.height);
    expect(f.top).toBeGreaterThanOrEqual(d.top); // top cloud under the status bar
    expect(f.top + f.height * 0.78).toBeLessThanOrEqual(panelTop + 0.5); // clouds and paws above the panel
    expect(f.left).toBeGreaterThanOrEqual(0);
    expect(f.left + f.width).toBeLessThanOrEqual(d.width); // right-hand clouds stay on screen
    expect(f.width).toBeGreaterThan(d.width * 0.5);
    // Back button (16..60 px) only meets the transparent top-left of the render (ear and tail start lower).
    expect(f.left + f.width * 0.15).toBeGreaterThan(60);
  });

  it('shows tobi_tasks in the «Задачи» header with the crown, cloud and raised paw visible', () => {
    const r = tobiRenders.tobi_tasks!;
    const headerHeight = roomHeaderHeight('section', d.height, d.top);
    const panelTop = headerHeight - ROOM_PANEL_OVERLAP;
    const f = computeRoomCharacterFrame({
      screenWidth: d.width,
      insetTop: d.top,
      headerHeight,
      aspect: r.width / r.height,
      scale: r.placement?.scale,
      offsetY: r.placement?.offsetY,
    });
    expect(f.width / f.height).toBeCloseTo(r.width / r.height);
    expect(f.top + f.height * 0.07).toBeGreaterThanOrEqual(d.top); // crown and cloud (below the transparent 7%) under the status bar
    expect(f.top + f.height * 0.72).toBeLessThanOrEqual(panelTop + 0.5); // raised paw above the panel
    expect(f.left).toBeGreaterThanOrEqual(0);
    expect(f.left + f.width).toBeLessThanOrEqual(d.width);
    expect(f.width).toBeGreaterThan(d.width * 0.55);
  });

  it('shows tobi_rewards in the «Награды» header with the star and heart cloud visible', () => {
    const r = tobiRenders.tobi_rewards!;
    const headerHeight = roomHeaderHeight('section', d.height, d.top);
    const panelTop = headerHeight - ROOM_PANEL_OVERLAP;
    const f = computeRoomCharacterFrame({
      screenWidth: d.width,
      insetTop: d.top,
      headerHeight,
      aspect: r.width / r.height,
      scale: r.placement?.scale,
      offsetY: r.placement?.offsetY,
    });
    expect(f.width / f.height).toBeCloseTo(r.width / r.height);
    expect(f.top + f.height * 0.027).toBeGreaterThanOrEqual(d.top); // ears under the status bar
    expect(f.top + f.height * 0.8).toBeLessThanOrEqual(panelTop + 0.5); // the whole star above the panel
    expect(f.left).toBeGreaterThanOrEqual(0);
    expect(f.left + f.width).toBeLessThanOrEqual(d.width); // heart cloud on screen
    expect(f.width).toBeGreaterThan(d.width * 0.5);
  });

  it('shows tobi_statistics in the «Статистика» header with the strokes, fist and face visible', () => {
    const r = tobiRenders.tobi_statistics!;
    const headerHeight = roomHeaderHeight('section', d.height, d.top);
    const panelTop = headerHeight - ROOM_PANEL_OVERLAP;
    const f = computeRoomCharacterFrame({
      screenWidth: d.width,
      insetTop: d.top,
      headerHeight,
      aspect: r.width / r.height,
      scale: r.placement?.scale,
      offsetY: r.placement?.offsetY,
    });
    expect(f.width / f.height).toBeCloseTo(r.width / r.height);
    expect(f.top).toBeGreaterThanOrEqual(d.top); // strokes above the fist under the status bar
    expect(f.top + f.height * 0.7).toBeLessThanOrEqual(panelTop + 0.5); // face above the panel
    expect(f.left).toBeGreaterThanOrEqual(0);
    expect(f.left + f.width).toBeLessThanOrEqual(d.width);
    expect(f.width).toBeGreaterThan(d.width * 0.55);
  });
});
