import { describe, expect, it } from 'vitest';
import { decodeFrame, stickOffset, createFrameBuffer } from './controller';

describe('firmware wire protocol', () => {
	it('decodes the pad index, button bytes and signed stick axes', () => {
		const state = decodeFrame(new Uint8Array([3, 0xa5, 0x29, 0x80, 0x7f]));
		expect(state).toEqual({
			padIndex: 3,
			buttons: {
				A: true,
				B: false,
				Z: true,
				START: false,
				UP: false,
				DOWN: true,
				LEFT: false,
				RIGHT: true,
				L: true,
				R: false,
				CUP: true,
				CDOWN: false,
				CLEFT: false,
				CRIGHT: true
			},
			x: -128,
			y: 127
		});
	});

	it('accepts legacy four-byte frames without a pad index', () => {
		const state = decodeFrame(new Uint8Array([0x5a, 0xd6, 0xff, 0]));
		expect(state).toEqual({
			padIndex: null,
			buttons: {
				A: false,
				B: true,
				Z: false,
				START: true,
				UP: true,
				DOWN: false,
				LEFT: true,
				RIGHT: false,
				L: false,
				R: true,
				CUP: false,
				CDOWN: true,
				CLEFT: true,
				CRIGHT: false
			},
			x: -1,
			y: 0
		});
	});

	it('ignores incomplete and oversized frames', () => {
		for (const length of [0, 1, 3, 6, 10]) {
			expect(decodeFrame(new Uint8Array(length))).toBeNull();
		}
	});

	it('maps and clamps stick travel to the well', () => {
		expect([-128, -90, -45, 0, 45, 90, 127].map(stickOffset)).toEqual([
			-38, -38, -19, 0, 19, 38, 38
		]);
	});
});

it('rejects invalid controller indices', () => {
	expect(decodeFrame(new Uint8Array([4, 0, 0, 0, 0]))).toBeNull();
	expect(decodeFrame(new Uint8Array([255, 0, 0, 0, 0]))).toBeNull();
});

it('coalesces by controller without dropping simultaneous controller updates', () => {
	const buffer = createFrameBuffer();
	for (let index = 0; index < 4; index++)
		buffer.push(decodeFrame(new Uint8Array([index, 0x80, 0, index, 0]))!);
	buffer.push(decodeFrame(new Uint8Array([2, 0x40, 0, 90, 0]))!);
	const frames = buffer.drain();
	expect(frames.map(([index]) => index)).toEqual([0, 1, 2, 3]);
	expect(frames[2][1].x).toBe(90);
	expect(frames[0][1].buttons.A).toBe(true);
	expect(buffer.drain()).toEqual([]);
	buffer.push(decodeFrame(new Uint8Array([0, 0, 0, 0]))!);
	expect(buffer.drain()[0][0]).toBe(0);
});
