// Mirror of cbroll/schemas.py (only the fields the renderer needs).

export type Animation = {
	enter: string;
	delay: number;
	duration: number;
	idle: string;
};

export type Layer = {
	id: string;
	kind: 'background' | 'photo' | 'cutout' | 'text' | 'shape' | 'texture';
	asset: string | null;
	text: string | null;
	font: string | null;
	font_size: number | null;
	color: string | null;
	bg: string | null;
	shape: string | null;
	x: number;
	y: number;
	w: number;
	h: number | null;
	rotation: number;
	z: number;
	depth: number;
	opacity: number;
	shadow: boolean;
	tape: boolean;
	blend: string | null;
	anim: Animation;
};

export type Scene = {
	id: string;
	index: number;
	text: string;
	status: string;
	background: string | null;
	layers: Layer[];
	camera: {move: string; strength: number};
};

export type TimelineEntry = {
	scene: string;
	duration_frames: number;
	transition_out: {type: string; frames: number};
};

export type RenderData = {
	project: {fps: number; width: number; height: number; palette: Record<string, string>};
	scenes: Scene[];
	timeline: {fps: number; entries: TimelineEntry[]};
	// Animate idle motion on twos (every 2nd frame) for a stop-motion feel.
	stepped: boolean;
};
