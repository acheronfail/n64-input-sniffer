export const BACKGROUND_KEY = 'n64-spy.background.v1';
export const DEFAULT_BACKGROUND = '#101720';
export const MINIMAL_KEY = 'n64-spy.minimal.v1';
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
