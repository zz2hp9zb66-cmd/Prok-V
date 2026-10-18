// Deterministic pseudo-random numbers so every render of a scene is identical.

export const hash = (s: string): number => {
	let h = 2166136261;
	for (let i = 0; i < s.length; i++) {
		h ^= s.charCodeAt(i);
		h = Math.imul(h, 16777619);
	}
	return h >>> 0;
};

export const rng = (seed: string) => {
	let a = hash(seed);
	return () => {
		a = (a + 0x6d2b79f5) | 0;
		let t = Math.imul(a ^ (a >>> 15), 1 | a);
		t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
		return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
	};
};

// Jagged polygon along the edges of a box, in percent, for a hand-torn look.
export const tornPolygon = (seed: string, roughness = 1.6, steps = 18): string => {
	const r = rng(seed);
	const j = () => (r() - 0.5) * roughness;
	const pts: string[] = [];
	for (let i = 0; i <= steps; i++) pts.push(`${(i / steps) * 100}% ${Math.max(0, j() + roughness / 2)}%`);
	for (let i = 0; i <= steps / 3; i++) pts.push(`${100 - Math.max(0, j() + roughness / 2)}% ${(i / (steps / 3)) * 100}%`);
	for (let i = steps; i >= 0; i--) pts.push(`${(i / steps) * 100}% ${100 - Math.max(0, j() + roughness / 2)}%`);
	for (let i = Math.floor(steps / 3); i >= 0; i--) pts.push(`${Math.max(0, j() + roughness / 2)}% ${(i / (steps / 3)) * 100}%`);
	return `polygon(${pts.join(',')})`;
};
