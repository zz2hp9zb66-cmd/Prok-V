import React from 'react';
import {Composition} from 'remotion';
import type {RenderData} from './types';
import {SceneView, totalFrames, Video} from './Video';

const EMPTY: RenderData = {
	project: {fps: 30, width: 1080, height: 1920, palette: {}},
	scenes: [],
	timeline: {fps: 30, entries: []},
	stepped: true,
};

type SceneProps = {data: RenderData; sceneId: string; isStatic: boolean};

export const Root: React.FC = () => (
	<>
		<Composition
			id="Video"
			component={Video}
			defaultProps={{data: EMPTY}}
			fps={30}
			width={1080}
			height={1920}
			durationInFrames={1}
			calculateMetadata={({props}) => ({
				durationInFrames: Math.max(1, totalFrames(props.data)),
				fps: props.data.project.fps,
				width: props.data.project.width,
				height: props.data.project.height,
			})}
		/>
		<Composition
			id="Scene"
			component={SceneView}
			defaultProps={{data: EMPTY, sceneId: '01', isStatic: true} as SceneProps}
			fps={30}
			width={1080}
			height={1920}
			durationInFrames={1}
			calculateMetadata={({props}) => {
				const entry = props.data.timeline.entries.find((e) => e.scene === props.sceneId);
				return {durationInFrames: props.isStatic ? 1 : entry?.duration_frames ?? 1, fps: props.data.project.fps};
			}}
		/>
	</>
);
