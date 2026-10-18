import {Easing, interpolate, spring} from 'remotion';
import type {Layer} from './types';
import {rng} from './random';

export type Pose = {
	dx: number;
	dy: number;
	scale: number;
	scaleY: number;
	rotate: number;
	opacity: number;
	clipRight: number; // percent hidden from the right, for wipe reveals
	chars: number | null; // visible characters for typewriter text
};

const REST: Pose = {dx: 0, dy: 0, scale: 1, scaleY: 1, rotate: 0, opacity: 1, clipRight: 0, chars: null};

const ease = Easing.bezier(0.2, 0.8, 0.2, 1);

// Entrance presets. `f` is frames since the layer's delay.
const enter = (layer: Layer, f: number, fps: number): Partial<Pose> => {
	const {duration} = layer.anim;
	const p = interpolate(f, [0, duration], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: ease});
	const sp = (damping: number) => spring({frame: f, fps, durationInFrames: duration * 1.6, config: {damping, mass: 0.8}});
	const r = rng(layer.id);
	const side = r() > 0.5 ? 1 : -1;
	switch (layer.anim.enter) {
		case 'none':
			return {};
		case 'fade':
			return {opacity: p, dy: (1 - p) * 40};
		case 'drop': {
			const s = sp(9);
			return {dy: (1 - s) * -900, rotate: (1 - s) * 14 * side, opacity: f >= 0 ? 1 : 0};
		}
		case 'slide_left':
			return {dx: (1 - p) * -1300, rotate: (1 - p) * -6};
		case 'slide_right':
			return {dx: (1 - p) * 1300, rotate: (1 - p) * 6};
		case 'slide_up':
			return {dy: (1 - p) * 1500, rotate: (1 - p) * 4 * side};
		case 'pop': {
			const s = sp(8);
			return {scale: 0.3 + 0.7 * s, opacity: Math.min(1, p * 4), rotate: (1 - s) * -10 * side};
		}
		case 'stamp': {
			const q = interpolate(f, [0, Math.max(4, duration / 2)], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.in(Easing.quad)});
			const shake = f > duration / 2 && f < duration / 2 + 6 ? Math.sin(f * 3) * 3 : 0;
			return {scale: 2.4 - 1.4 * q, opacity: q > 0 ? 1 : 0, rotate: shake};
		}
		case 'wipe':
			return {clipRight: (1 - p) * 100};
		case 'unfold':
			return {scaleY: Math.max(0.001, sp(12)), opacity: Math.min(1, p * 3)};
		case 'stop_motion': {
			// Three hand-placed jumps, like a cut-out moved between exposures.
			const step = Math.min(3, Math.floor(p * 4));
			const k = 1 - step / 3;
			return {dx: k * 220 * side, dy: k * 160, rotate: k * 12 * side, opacity: f >= 0 ? 1 : 0};
		}
		case 'typewriter':
			return {chars: Math.floor(p * (layer.text?.length ?? 0))};
		default:
			return {opacity: p};
	}
};

// Motion after landing. `t` is frames since the entrance finished.
const idle = (layer: Layer, t: number): Partial<Pose> => {
	const r = rng(layer.id + 'idle');
	const phase = r() * Math.PI * 2;
	const amp = 0.5 + layer.depth;
	switch (layer.anim.idle) {
		case 'drift':
			return {dx: Math.sin(t / 55 + phase) * 7 * amp, dy: Math.cos(t / 70 + phase) * 6 * amp};
		case 'sway':
			return {rotate: Math.sin(t / 22 + phase) * 1.4};
		case 'breathe':
			return {scale: 1 + Math.sin(t / 34 + phase) * 0.018};
		case 'jitter':
			// Stop-motion boil: tiny random offsets every few frames.
			{
				const k = rng(`${layer.id}:${Math.floor(t / 4)}`);
				return {dx: (k() - 0.5) * 5, dy: (k() - 0.5) * 5, rotate: (k() - 0.5) * 0.8};
			}
		default:
			return {};
	}
};

export const poseAt = (layer: Layer, frame: number, fps: number, stepped: boolean, isStatic: boolean): Pose => {
	if (isStatic) return REST;
	const f = frame - layer.anim.delay;
	if (f < 0 && layer.anim.enter !== 'none') {
		const pre = enter(layer, 0, fps);
		return {...REST, ...pre, opacity: layer.anim.enter === 'typewriter' ? 1 : 0};
	}
	const a = enter(layer, f, fps);
	const tf = stepped ? Math.floor(frame / 2) * 2 : frame;
	const b = idle(layer, Math.max(0, tf - layer.anim.delay - layer.anim.duration));
	return {
		dx: (a.dx ?? 0) + (b.dx ?? 0),
		dy: (a.dy ?? 0) + (b.dy ?? 0),
		scale: (a.scale ?? 1) * (b.scale ?? 1),
		scaleY: a.scaleY ?? 1,
		rotate: (a.rotate ?? 0) + (b.rotate ?? 0),
		opacity: a.opacity ?? 1,
		clipRight: a.clipRight ?? 0,
		chars: a.chars ?? null,
	};
};

export type CameraPose = {scale: number; x: number; y: number; rotate: number};

// Whole-scene camera. Layers add parallax on top of it according to depth.
export const cameraAt = (move: string, strength: number, frame: number, duration: number, isStatic: boolean): CameraPose => {
	if (isStatic) return {scale: 1, x: 0, y: 0, rotate: 0};
	const p = interpolate(frame, [0, duration], [0, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp', easing: Easing.inOut(Easing.sin)});
	const s = strength;
	switch (move) {
		case 'push_in':
			return {scale: 1 + 0.09 * s * p, x: 0, y: -20 * s * p, rotate: 0};
		case 'pull_out':
			return {scale: 1.1 - 0.08 * s * p, x: 0, y: 0, rotate: 0};
		case 'pan_left':
			return {scale: 1.07, x: (0.5 - p) * 90 * s, y: 0, rotate: 0};
		case 'pan_right':
			return {scale: 1.07, x: (p - 0.5) * 90 * s, y: 0, rotate: 0};
		case 'tilt_up':
			return {scale: 1.07, x: 0, y: (p - 0.5) * 110 * s, rotate: 0};
		case 'dutch':
			return {scale: 1.06 + 0.04 * p, x: 0, y: 0, rotate: (p - 0.5) * 2.4 * s};
		default:
			return {scale: 1, x: 0, y: 0, rotate: 0};
	}
};
