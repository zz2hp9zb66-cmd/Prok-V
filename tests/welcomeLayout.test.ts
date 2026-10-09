import { computeTobiFrame, TOBI_WAVE_ASPECT, TOBI_WAVE_BOUNDS } from '@/features/onboarding/welcomeLayout';

/**
 * Screen sizes and safe areas of the target iPhones. Text/button edges follow
 * the welcome layout: title starts under the status bar, button sits above the
 * home indicator with the step dots under it.
 */
const DEVICES = {
  'iPhone SE': { width: 375, height: 667, top: 20, bottom: 0 },
  'iPhone 13 mini': { width: 375, height: 812, top: 50, bottom: 34 },
  'iPhone 15': { width: 393, height: 852, top: 59, bottom: 34 },
  'iPhone 15 Pro Max': { width: 430, height: 932, top: 59, bottom: 34 },
};

const TEXT_BLOCK = 16 + 52 + 8 + 3 * 24; // padding + display title + gap + 3 lead lines
const FOOTER = 56 + 20 + 10 + 16; // button + gap + dots + padding above the safe area

describe.each(Object.entries(DEVICES))('welcome layout on %s', (_, d) => {
  const textBottom = d.top + TEXT_BLOCK;
  const buttonTop = d.height - Math.max(d.bottom, 16) - FOOTER;
  const frame = computeTobiFrame({ width: d.width, height: d.height, textBottom, buttonTop });
  const b = TOBI_WAVE_BOUNDS;
  const ears = frame.top + frame.height * b.top;
  const feet = frame.top + frame.height * b.bottom;
  const charLeft = frame.left + frame.width * b.left;
  const charRight = frame.left + frame.width * b.right;

  it('keeps the render proportions', () => {
    expect(frame.width / frame.height).toBeCloseTo(TOBI_WAVE_ASPECT);
  });

  it('makes TOBI the main element (large character)', () => {
    expect((feet - ears) / d.height).toBeGreaterThan(0.4);
  });

  it('does not overlap the title or reach the button', () => {
    expect(ears).toBeGreaterThan(textBottom);
    expect(feet).toBeLessThan(buttonTop);
  });

  it('keeps the whole character on screen horizontally', () => {
    expect(charLeft).toBeGreaterThanOrEqual(0);
    expect(charRight).toBeLessThanOrEqual(d.width);
  });
});
