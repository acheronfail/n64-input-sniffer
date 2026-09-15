export const BACKGROUND_KEY = 'n64-spy.background.v1';
export const DEFAULT_BACKGROUND = 'transparent';
export const DEFAULT_BACKGROUND_COLOR = '#00ff00';
export const MINIMAL_KEY = 'n64-spy.minimal.v1';
export const MINIMAL_LATENCY_KEY = 'n64-spy.minimal-latency.v1';
export const MINIMAL_CONNECTION_KEY = 'n64-spy.minimal-connection.v1';
export const SETTINGS_KEY = 'n64-spy.controllers.v1';
export const ALL_CONTROLLERS = [0, 1, 2, 3];

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
