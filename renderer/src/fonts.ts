import {useEffect, useState} from 'react';
import {continueRender, delayRender} from 'remotion';
import '@fontsource/oswald/700.css';
import '@fontsource/bebas-neue/400.css';
import '@fontsource/ibm-plex-mono/500.css';
import '@fontsource/playfair-display/700-italic.css';
import '@fontsource/rubik-mono-one/400.css';

export const FONTS: Record<string, React.CSSProperties> = {
	headline: {fontFamily: 'Oswald', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '-0.02em', lineHeight: 0.9},
	poster: {fontFamily: '"Bebas Neue", Oswald', fontWeight: 400, lineHeight: 0.82, letterSpacing: '0.01em'},
	label: {fontFamily: '"IBM Plex Mono"', fontWeight: 500, textTransform: 'uppercase', letterSpacing: '0.06em'},
	caption: {fontFamily: '"Playfair Display"', fontWeight: 700, fontStyle: 'italic'},
	stamp: {fontFamily: '"Rubik Mono One"', fontWeight: 400, letterSpacing: '0.04em'},
};

const SPECS = [
	'700 100px Oswald',
	'400 100px "Bebas Neue"',
	'500 100px "IBM Plex Mono"',
	'italic 700 100px "Playfair Display"',
	'400 100px "Rubik Mono One"',
];

// Hold the render until every face (Latin + Cyrillic subsets) is loaded.
export const useFonts = () => {
	const [handle] = useState(() => delayRender('fonts'));
	useEffect(() => {
		Promise.all(SPECS.map((s) => document.fonts.load(s, 'AaЯя19')))
			.then(() => continueRender(handle))
			.catch(() => continueRender(handle));
	}, [handle]);
};
