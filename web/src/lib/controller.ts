// Keep these masks in sync with packState() in include/n64_decoder.h.
export const B0 = {
	A: 0x80,
	B: 0x40,
	Z: 0x20,
	START: 0x10,
	UP: 0x08,
	DOWN: 0x04,
	LEFT: 0x02,
	RIGHT: 0x01
};
export const B1 = { L: 0x20, R: 0x10, CUP: 0x08, CDOWN: 0x04, CLEFT: 0x02, CRIGHT: 0x01 };
type Button = keyof typeof B0 | keyof typeof B1;
export type ControllerState = {
	padIndex: number | null;
	decodedMs?: number;
	buttons: Record<Button, boolean>;
	x: number;
	y: number;
};

export function decodeFrame(raw: Uint8Array): ControllerState | null {
	if (raw.length !== 4 && raw.length !== 5 && raw.length !== 13) return null;
	const offset = raw.length >= 5 ? 1 : 0;
	if (offset && raw[0] > 3) return null;
	const buttons = {} as Record<Button, boolean>;
	for (const [id, mask] of Object.entries(B0)) buttons[id as Button] = !!(raw[offset] & mask);
	for (const [id, mask] of Object.entries(B1)) buttons[id as Button] = !!(raw[offset + 1] & mask);
	return {
		padIndex: offset ? raw[0] : null,
		...(raw.length === 13
			? {
					decodedMs:
						Number(new DataView(raw.buffer, raw.byteOffset, raw.byteLength).getBigUint64(5, true)) /
						1000
				}
			: {}),
		buttons,
		x: (raw[offset + 2] << 24) >> 24,
		y: (raw[offset + 3] << 24) >> 24
	};
}

export function emptyState(): ControllerState {
	return decodeFrame(new Uint8Array(4))!;
}

export function stickOffset(value: number): number {
	return Math.max(-1, Math.min(1, value / 90)) * 38;
}

// Keep one pending frame per controller. Legacy frames belong to controller 1.
export function createFrameBuffer() {
	const pending = new Map<number, ControllerState>();
	return {
		push(frame: ControllerState) {
			pending.set(frame.padIndex ?? 0, frame);
		},
		drain() {
			const frames = [...pending.entries()];
			pending.clear();
			return frames;
		}
	};
}
