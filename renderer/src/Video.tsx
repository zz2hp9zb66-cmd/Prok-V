import React from 'react';
import {TransitionSeries} from '@remotion/transitions';
import {useVideoConfig} from 'remotion';
import {Collage} from './Collage';
import {useFonts} from './fonts';
import {makeTransition} from './transitions';
import type {RenderData} from './types';

export const totalFrames = (data: RenderData) => {
	const entries = data.timeline.entries;
	const transitions = entries.slice(0, -1).reduce((s, e) => s + e.transition_out.frames, 0);
	return entries.reduce((s, e) => s + e.duration_frames, 0) - transitions;
};

export const Video: React.FC<{data: RenderData}> = ({data}) => {
	useFonts();
	const {width, height} = useVideoConfig();
	const byId = Object.fromEntries(data.scenes.map((s) => [s.id, s]));
	const entries = data.timeline.entries;
	return (
		<TransitionSeries>
			{entries.flatMap((e, i) => {
				const items = [
					<TransitionSeries.Sequence key={e.scene} durationInFrames={e.duration_frames}>
						<Collage scene={byId[e.scene]} duration={e.duration_frames} isStatic={false} stepped={data.stepped} />
					</TransitionSeries.Sequence>,
				];
				if (i < entries.length - 1) {
					const t = makeTransition(e.transition_out.type, e.transition_out.frames, e.scene, width, height);
					items.push(<TransitionSeries.Transition key={`${e.scene}-t`} timing={t.timing} presentation={t.presentation} />);
				}
				return items;
			})}
		</TransitionSeries>
	);
};

// A single scene, either frozen in its final layout (storyboard) or animated.
export const SceneView: React.FC<{data: RenderData; sceneId: string; isStatic: boolean}> = ({data, sceneId, isStatic}) => {
	useFonts();
	const scene = data.scenes.find((s) => s.id === sceneId)!;
	const entry = data.timeline.entries.find((e) => e.scene === sceneId)!;
	return <Collage scene={scene} duration={entry.duration_frames} isStatic={isStatic} stepped={data.stepped} />;
};
