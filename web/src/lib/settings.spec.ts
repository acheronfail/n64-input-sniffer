import { expect, it } from 'vitest';
import {
	DEFAULT_MINIMAL_STATUS_SIZE,
	parseMinimalStatusSize,
	parseVisibility,
	parseTheme
} from './settings';

it('restores minimal status sizes and rejects invalid saved values', () => {
	for (const size of [12, 24, 40, 64]) {
		expect(parseMinimalStatusSize(JSON.stringify(size))).toBe(size);
	}
	for (const raw of [null, '{', 'null', '{}', '"24"', '0', '11', '65', '24.5']) {
		expect(parseMinimalStatusSize(raw)).toBe(DEFAULT_MINIMAL_STATUS_SIZE);
	}
});
it('restores arbitrary controller selections including none', () => {
	expect(parseVisibility('[2]')).toEqual([2]);
	expect(parseVisibility('[3,0,3]')).toEqual([0, 3]);
	expect(parseVisibility('[]')).toEqual([]);
});
it('recovers from missing, malformed or out-of-range saved settings', () => {
	for (const raw of [null, '{', '{}', '[4]', '[-1]', '[1.5]', '["1"]']) {
		expect(parseVisibility(raw)).toEqual([0, 1, 2, 3]);
	}
});

it('restores themes and falls back to classic for invalid saved preferences', () => {
	for (const theme of ['classic', 'enlarged', 'buttons-only']) {
		expect(parseTheme(JSON.stringify(theme))).toBe(theme);
	}
	for (const raw of [null, '{', 'null', '{}', '"unknown"']) {
		expect(parseTheme(raw)).toBe('classic');
	}
});
