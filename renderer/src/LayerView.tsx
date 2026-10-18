import React from 'react';
import {Img, staticFile, useCurrentFrame, useVideoConfig} from 'remotion';
import {FONTS} from './fonts';
import {type CameraPose, poseAt} from './motion';
import {rng, tornPolygon} from './random';
import type {Layer} from './types';

const SHADOW = 'drop-shadow(0px 14px 16px rgba(0,0,0,0.35)) drop-shadow(0px 2px 3px rgba(0,0,0,0.3))';

const Tape: React.FC<{seed: string}> = ({seed}) => {
	const r = rng(seed + 'tape');
	const piece = (left: string, top: string, rot: number): React.CSSProperties => ({
		position: 'absolute',
		left,
		top,
		width: 150,
		height: 46,
		transform: `translate(-50%, -50%) rotate(${rot}deg)`,
		background: 'rgba(236, 226, 196, 0.78)',
		boxShadow: '0 1px 2px rgba(0,0,0,0.15)',
		clipPath: tornPolygon(seed + left, 6, 8),
	});
	return (
		<>
			<div style={piece(`${8 + r() * 6}%`, '2%', -35 + r() * 10)} />
			<div style={piece(`${86 + r() * 6}%`, '2%', 32 + r() * 10)} />
		</>
	);
};

const TextBody: React.FC<{layer: Layer; chars: number | null}> = ({layer, chars}) => {
	const text = layer.text ?? '';
	const shown = chars === null ? text : text.slice(0, chars);
	const font = FONTS[layer.font ?? 'label'] ?? FONTS.label;
	const strip = layer.bg !== null;
	return (
		<div
			style={{
				...font,
				fontSize: layer.font_size ?? 40,
				color: layer.color ?? '#111',
				whiteSpace: 'pre',
				textAlign: 'center',
				background: strip ? layer.bg! : undefined,
				padding: strip ? '0.32em 0.7em 0.36em' : undefined,
				clipPath: strip ? tornPolygon(layer.id, 3.5, 16) : undefined,
				textShadow: !strip && layer.font === 'headline' ? '6px 6px 0 rgba(0,0,0,0.85)' : undefined,
			}}
		>
			{/* keep box width stable while typing */}
			<span>{shown}</span>
			<span style={{visibility: 'hidden'}}>{text.slice(shown.length)}</span>
		</div>
	);
};

export const LayerView: React.FC<{layer: Layer; cam: CameraPose; isStatic: boolean; stepped: boolean}> = ({layer, cam, isStatic, stepped}) => {
	const frame = useCurrentFrame();
	const {fps} = useVideoConfig();
	const pose = poseAt(layer, frame, fps, stepped, isStatic);

	// Parallax: near layers move further than the camera, far ones lag behind it.
	const k = (layer.depth - 0.5) * 1.4;
	const px = cam.x * k;
	const py = cam.y * k;
	const pScale = 1 + (cam.scale - 1) * k;

	if (layer.kind === 'texture') {
		// Film grain: re-position the grain plate on every other frame.
		const r = rng(`grain${Math.floor(frame / 2)}`);
		const ox = isStatic ? 0 : (r() - 0.5) * 80;
		const oy = isStatic ? 0 : (r() - 0.5) * 80;
		return (
			<Img
				src={staticFile(layer.asset!)}
				style={{
					position: 'absolute',
					inset: -60,
					width: 'calc(100% + 120px)',
					height: 'calc(100% + 120px)',
					transform: `translate(${ox}px, ${oy}px)`,
					opacity: layer.opacity,
					mixBlendMode: (layer.blend ?? 'overlay') as React.CSSProperties['mixBlendMode'],
				}}
			/>
		);
	}

	const box: React.CSSProperties = {
		position: 'absolute',
		left: layer.x + px + pose.dx,
		top: layer.y + py + pose.dy,
		width: layer.kind === 'text' ? undefined : layer.w,
		transform: `translate(-50%, -50%) rotate(${layer.rotation + pose.rotate}deg) scale(${pose.scale * pScale}, ${pose.scale * pScale * pose.scaleY})`,
		opacity: layer.opacity * pose.opacity,
		filter: layer.shadow ? SHADOW : undefined,
		clipPath: pose.clipRight > 0 ? `inset(-10% ${pose.clipRight}% -10% -10%)` : undefined,
		mixBlendMode: (layer.blend ?? undefined) as React.CSSProperties['mixBlendMode'],
	};

	if (layer.kind === 'shape') {
		return (
			<div style={{...box, height: layer.h ?? layer.w}}>
				<div style={{width: '100%', height: '100%', background: layer.bg ?? '#1d3f8f', clipPath: tornPolygon(layer.id, 1.2, 28)}} />
			</div>
		);
	}

	if (layer.kind === 'text') {
		return (
			<div style={box}>
				<TextBody layer={layer} chars={pose.chars} />
			</div>
		);
	}

	return (
		<div style={box}>
			<Img src={staticFile(layer.asset!)} style={{width: '100%', display: 'block'}} />
			{layer.tape ? <Tape seed={layer.id} /> : null}
		</div>
	);
};
