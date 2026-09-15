export const BACKGROUND_KEY = 'n64-spy.background.v1';
export const DEFAULT_BACKGROUND = 'transparent';
export const DEFAULT_BACKGROUND_COLOR = '#00ff00';
export const MINIMAL_KEY = 'n64-spy.minimal.v1';
export const MINIMAL_LATENCY_KEY = 'n64-spy.minimal-latency.v1';
export const MINIMAL_CONNECTION_KEY = 'n64-spy.minimal-connection.v1';
export const MINIMAL_STATUS_SIZE_KEY = 'n64-spy.minimal-status-size.v1';
export const DEFAULT_MINIMAL_STATUS_SIZE = 24;
export const MIN_MINIMAL_STATUS_SIZE = 12;
export const MAX_MINIMAL_STATUS_SIZE = 64;

export function parseMinimalStatusSize(raw: string | null): number {
	try {
		const value: unknown = JSON.parse(raw ?? 'null');
		return typeof value === 'number' &&
			Number.isInteger(value) &&
			value >= MIN_MINIMAL_STATUS_SIZE &&
			value <= MAX_MINIMAL_STATUS_SIZE
			? value
			: DEFAULT_MINIMAL_STATUS_SIZE;
	} catch {
		return DEFAULT_MINIMAL_STATUS_SIZE;
	}
}

export const SETTINGS_KEY = 'n64-spy.controllers.v1';
export const ALL_CONTROLLERS = [0, 1, 2, 3];
export const PLAYER_NAMES_KEY = 'n64-spy.player-names.v1';
export function parsePlayerNames(raw: string | null): string[] {
	let value: unknown;
	try {
		value = JSON.parse(raw ?? 'null');
	} catch {
		/* Use default names. */
	}
	return ALL_CONTROLLERS.map((index) => {
		const name: unknown = Array.isArray(value) ? value[index] : undefined;
		return typeof name === 'string' && name.trim() ? name.trim().slice(0, 24) : `Pad ${index + 1}`;
	});
}
export const STACKING_KEY = 'n64-spy.stacking.v1';
export const STACKING_OPTIONS = [
	{ value: 'normal', label: 'Normal' },
	{ value: 'vertical', label: 'Vertical' },
	{ value: 'horizontal', label: 'Horizontal' }
] as const;
export type ControllerStacking = (typeof STACKING_OPTIONS)[number]['value'];

export function parseStacking(raw: string | null): ControllerStacking {
	try {
		const value: unknown = JSON.parse(raw ?? 'null');
		return STACKING_OPTIONS.find((option) => option.value === value)?.value ?? 'normal';
	} catch {
		return 'normal';
	}
}

export function parseVisibility(raw: string | null): number[] {
	if (raw === null) return [...ALL_CONTROLLERS];
	try {
		const value: unknown = JSON.parse(raw);
		if (
			!Array.isArray(value) ||
			!value.every((index) => Number.isInteger(index) && index >= 0 && index < 4)
		) {
			return [...ALL_CONTROLLERS];
		}
		return [...new Set(value)].sort();
	} catch {
		return [...ALL_CONTROLLERS];
	}
}

export const THEME_KEY = 'n64-spy.theme.v1';
export const THEMES = [
	{ value: 'classic', label: 'Classic' },
	{ value: 'enlarged', label: 'Enlarged' },
	{ value: 'buttons-only', label: 'Buttons only' }
] as const;
export type ControllerTheme = (typeof THEMES)[number]['value'];
export function parseTheme(raw: string | null): ControllerTheme {
	try {
		const value: unknown = JSON.parse(raw ?? 'null');
		return THEMES.find((theme) => theme.value === value)?.value ?? 'classic';
	} catch {
		return 'classic';
	}
}
