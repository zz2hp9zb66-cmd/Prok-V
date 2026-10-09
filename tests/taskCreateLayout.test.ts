import { computeTaskCreateTobiFrame, TOBI_HABIT_CREATE_ASPECT } from '@/features/habits/taskCreateLayout';

const DEVICES = {
  'iPhone SE': { width: 375, height: 667, top: 20 },
  'iPhone 13 mini': { width: 375, height: 812, top: 50 },
  'iPhone 15': { width: 393, height: 852, top: 59 },
  'iPhone 15 Pro Max': { width: 430, height: 932, top: 59 },
};
const PANEL_OVERLAP = 32;
const BACK_BUTTON = { left: 16, size: 44 };

describe.each(Object.entries(DEVICES))('task creation TOBI on %s', (_, d) => {
  // Same header height rule as HabitCreateView.
  const sceneHeight = Math.round(Math.min(Math.max(d.height * 0.26, 170), 280)) + d.top;
  const panelTop = sceneHeight - PANEL_OVERLAP;
  const f = computeTaskCreateTobiFrame({ screenWidth: d.width, insetTop: d.top, panelTop });

  it('keeps proportions and fits the screen width', () => {
    expect(f.width / f.height).toBeCloseTo(TOBI_HABIT_CREATE_ASPECT);
    expect(f.left).toBeGreaterThanOrEqual(0);
    expect(f.left + f.width).toBeLessThanOrEqual(d.width);
  });

  it('never cuts the head: the render starts under the status bar', () => {
    expect(f.top).toBeGreaterThanOrEqual(d.top);
  });

  it('keeps the notebook visible above the panel (≈94% of the render)', () => {
    expect(f.top + f.height * 0.94).toBeLessThanOrEqual(panelTop);
    expect(f.top + f.height).toBeGreaterThan(panelTop); // hem tucks behind the panel
  });

  it('is large enough to read the face, paws and notebook', () => {
    expect(f.width).toBeGreaterThan(d.width * 0.55);
  });

  it('does not reach the back button area (transparent top-left of the render)', () => {
    // The render is empty left of ≈30% of its width above its middle (only the tail lives lower).
    const emptyRight = f.left + f.width * 0.3;
    const buttonBottom = d.top + 8 + BACK_BUTTON.size;
    const tailTop = f.top + f.height * 0.5;
    expect(BACK_BUTTON.left + BACK_BUTTON.size <= emptyRight || buttonBottom <= tailTop).toBe(true);
  });
});
