/**
 * Sound & haptic feedback — spec §21.
 * Full sound design and haptics come after the test build. Business logic
 * emits these semantic events; the implementation can be swapped later
 * without touching domain code.
 */
export type FeedbackEvent = 'habitCompleted' | 'rewardRedeemed';

export interface FeedbackService {
  play(event: FeedbackEvent): void;
}

export const noopFeedback: FeedbackService = {
  play: () => {},
};
