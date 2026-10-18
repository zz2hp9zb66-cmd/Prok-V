import React, {useMemo} from 'react';
import {AbsoluteFill, interpolate} from 'remotion';
import {linearTiming, type TransitionPresentation, type TransitionPresentationComponentProps, type TransitionTiming} from '@remotion/transitions';
import {fade} from '@remotion/transitions/fade';
import {slide} from '@remotion/transitions/slide';
import {wipe} from '@remotion/transitions/wipe';
import {rng} from './random';

type TearProps = {seed: string; width: number; height: number};

// The next scene is revealed behind a torn paper edge sweeping right-to-left.
const PaperTear: React.FC<TransitionPresentationComponentProps<TearProps>> = ({children, presentationDirection, presentationProgress, passedProps}) => {
	const {seed, width, height} = passedProps;
	const edge = useMemo(() => {
		const r = rng(seed);
		const n = 40;
		return Array.from({length: n + 1}, (_, i) => ({y: (i / n) * height, j: (r() - 0.5) * 70 + Math.sin(i * 0.7) * 25}));
	}, [seed, height]);
	if (presentationDirection === 'exiting') return <AbsoluteFill>{children}</AbsoluteFill>;
	const x0 = interpolate(presentationProgress, [0, 1], [width + 120, -180]);
	const poly = (offset: number) =>
		`polygon(${[`${width + 200}px 0px`, ...edge.map((p) => `${x0 + p.j - offset + p.y * 0.12}px ${p.y}px`), `${width + 200}px ${height}px`].join(',')})`;
	return (
		<AbsoluteFill>
			<AbsoluteFill style={{background: '#f7f2e6', clipPath: poly(22), filter: 'drop-shadow(-8px 0 10px rgba(0,0,0,0.35))'}} />
			<AbsoluteFill style={{clipPath: poly(0)}}>{children}</AbsoluteFill>
		</AbsoluteFill>
	);
};

const paperTear = (props: TearProps): TransitionPresentation<TearProps> => ({component: PaperTear, props});

// Exiting scene rushes towards the viewer, the new one settles in.
const ZoomThrough: React.FC<TransitionPresentationComponentProps<Record<string, never>>> = ({children, presentationDirection, presentationProgress}) => {
	const p = presentationProgress;
	const style: React.CSSProperties =
		presentationDirection === 'exiting'
			? {transform: `scale(${1 + p * 0.6})`, opacity: 1 - p}
			: {transform: `scale(${0.82 + p * 0.18})`, opacity: Math.min(1, p * 2)};
	return <AbsoluteFill style={style}>{children}</AbsoluteFill>;
};

const zoomThrough = (): TransitionPresentation<Record<string, never>> => ({component: ZoomThrough, props: {}});

// eslint-disable-next-line @typescript-eslint/no-explicit-any
type AnyPresentation = TransitionPresentation<any>;

export const makeTransition = (
	type: string,
	frames: number,
	seed: string,
	width: number,
	height: number,
): {timing: TransitionTiming; presentation: AnyPresentation} => {
	const timing = linearTiming({durationInFrames: frames});
	switch (type) {
		case 'slide':
			return {timing, presentation: slide({direction: 'from-bottom'})};
		case 'wipe':
			return {timing, presentation: wipe({direction: 'from-left'})};
		case 'paper_tear':
			return {timing, presentation: paperTear({seed, width, height})};
		case 'zoom':
			return {timing, presentation: zoomThrough()};
		default:
			return {timing, presentation: fade()};
	}
};
