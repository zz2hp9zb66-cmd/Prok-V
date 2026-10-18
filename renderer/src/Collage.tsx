import React from 'react';
import {AbsoluteFill, Img, staticFile, useCurrentFrame} from 'remotion';
import {LayerView} from './LayerView';
import {cameraAt} from './motion';
import type {Scene} from './types';

export const Collage: React.FC<{scene: Scene; duration: number; isStatic: boolean; stepped: boolean}> = ({scene, duration, isStatic, stepped}) => {
	const frame = useCurrentFrame();
	const cam = cameraAt(scene.camera.move, scene.camera.strength, frame, duration, isStatic);
	const layers = [...scene.layers].sort((a, b) => a.z - b.z);
	return (
		<AbsoluteFill style={{background: '#efe6d2', overflow: 'hidden'}}>
			<AbsoluteFill style={{transform: `translate(${cam.x}px, ${cam.y}px) scale(${cam.scale}) rotate(${cam.rotate}deg)`}}>
				{scene.background ? (
					<Img src={staticFile(scene.background)} style={{position: 'absolute', inset: -80, width: 'calc(100% + 160px)', height: 'calc(100% + 160px)', objectFit: 'cover'}} />
				) : null}
				{layers
					.filter((l) => l.kind !== 'texture')
					.map((l) => (
						<LayerView key={l.id} layer={l} cam={cam} isStatic={isStatic} stepped={stepped} />
					))}
			</AbsoluteFill>
			{layers
				.filter((l) => l.kind === 'texture')
				.map((l) => (
					<LayerView key={l.id} layer={l} cam={cam} isStatic={isStatic} stepped={stepped} />
				))}
		</AbsoluteFill>
	);
};
