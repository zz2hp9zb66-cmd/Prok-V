// Render storyboard stills or the final video from a props file written by cbroll.
//
//   node scripts/render.mjs --project <dir> --props <file> --stills <outdir> [--scenes 01,03]
//   node scripts/render.mjs --project <dir> --props <file> --video <out.mp4>
//   node scripts/render.mjs --project <dir> --props <file> --scene-video 02 <out.mp4>
//
// CBROLL_BROWSER may point at a local Chrome/Chromium; otherwise Remotion downloads its own.

import {bundle} from '@remotion/bundler';
import {renderMedia, renderStill, selectComposition} from '@remotion/renderer';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {fileURLToPath} from 'node:url';

const args = process.argv.slice(2);
const opt = (name) => {
	const i = args.indexOf(`--${name}`);
	return i >= 0 ? args[i + 1] : undefined;
};

const projectDir = path.resolve(opt('project'));
const data = JSON.parse(fs.readFileSync(path.resolve(opt('props')), 'utf8'));
const here = path.dirname(fileURLToPath(import.meta.url));
const browserExecutable = process.env.CBROLL_BROWSER || null;
const concurrency = Number(process.env.CBROLL_CONCURRENCY || Math.max(1, os.cpus().length - 1));

const t0 = Date.now();
const serveUrl = await bundle({
	entryPoint: path.join(here, '..', 'src', 'index.ts'),
	publicDir: projectDir,
});
console.log(`bundled in ${((Date.now() - t0) / 1000).toFixed(1)}s`);

const common = {serveUrl, browserExecutable, chromiumOptions: {gl: 'swangle'}};

const stillsDir = opt('stills');
if (stillsDir) {
	fs.mkdirSync(stillsDir, {recursive: true});
	const only = opt('scenes')?.split(',');
	for (const scene of data.scenes) {
		if (only && !only.includes(scene.id)) continue;
		const inputProps = {data, sceneId: scene.id, isStatic: true};
		const composition = await selectComposition({...common, id: 'Scene', inputProps});
		const output = path.join(stillsDir, `scene_${scene.id}.png`);
		await renderStill({...common, composition, inputProps, output, frame: 0, overwrite: true});
		console.log(`still ${output}`);
	}
}

const progress = ({progress}) => {
	process.stdout.write(`\r${Math.round(progress * 100)}%`);
};

const video = opt('video');
if (video) {
	const inputProps = {data};
	const composition = await selectComposition({...common, id: 'Video', inputProps});
	await renderMedia({
		...common,
		composition,
		inputProps,
		codec: 'h264',
		crf: 18,
		pixelFormat: 'yuv420p',
		muted: true,
		concurrency,
		outputLocation: video,
		onProgress: progress,
	});
	console.log(`\nvideo ${video} (${composition.durationInFrames} frames)`);
}

const sceneVideoIdx = args.indexOf('--scene-video');
if (sceneVideoIdx >= 0) {
	const sceneId = args[sceneVideoIdx + 1];
	const output = args[sceneVideoIdx + 2];
	const inputProps = {data, sceneId, isStatic: false};
	const composition = await selectComposition({...common, id: 'Scene', inputProps});
	await renderMedia({...common, composition, inputProps, codec: 'h264', crf: 18, pixelFormat: 'yuv420p', muted: true, concurrency, outputLocation: output, onProgress: progress});
	console.log(`\nscene video ${output}`);
}
