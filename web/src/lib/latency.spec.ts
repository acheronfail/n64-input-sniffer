import { describe, expect, it } from 'vitest';
import { createLatencyTracker } from './latency';
import { decodeFrame } from './controller';

describe('input latency', () => {
	it('measures idle replies and keeps input and link smoothing separate', () => {
		const tracker = createLatencyTracker();
		tracker.probe(100);
		tracker.receive('sync:1:1105000:1107000', 112);
		expect(tracker.reading(112)).toEqual({ ms: 5, stale: false, source: 'link' });
		tracker.input(1200, 250);
		tracker.probe(300);
		tracker.receive('sync:2:1305000:1307000', 312);
		expect(tracker.reading(312)).toEqual({ ms: 50, stale: false, source: 'input' });
		tracker.probe(4000);
		tracker.receive('sync:3:5005000:5007000', 4027);
		expect(tracker.reading(4027)).toEqual({ ms: 20, stale: false, source: 'link' });
		expect(tracker.reading(7028).stale).toBe(true);
	});
	it('decodes a timestamp beyond the 32-bit microsecond rollover from a subarray', () => {
		const backing = new Uint8Array(20);
		const packet = backing.subarray(3, 16);
		packet.set([2, 0x80, 0, 128, 127]);
		new DataView(backing.buffer).setBigUint64(8, 5000000000n, true);
		expect(decodeFrame(packet)).toMatchObject({ padIndex: 2, x: -128, y: 127, decodedMs: 5000000 });
		expect(decodeFrame(new Uint8Array(12))).toBeNull();
	});
	it('includes queue delay and removes clock offset and reply processing time', () => {
		const tracker = createLatencyTracker();
		expect(tracker.probe(100)).toBe('sync:1');
		expect(tracker.receive('sync:1:1105000:1107000', 112)).toBe(true);
		tracker.input(1150, 174);
		expect(tracker.reading(174)).toEqual({ ms: 24, stale: false, source: 'input' });
		expect(tracker.reading(3175)).toEqual({ ms: 5, stale: true, source: 'link' });
		expect(tracker.reading(30112).ms).toBeNull();
	});
	it('rejects snapshots, legacy frames, unmatched replies and invalid timing', () => {
		const tracker = createLatencyTracker();
		tracker.probe(100);
		expect(tracker.receive('sync:2:1105000:1105000', 110)).toBe(false);
		expect(tracker.receive('sync:1:1105000:1105000', 110)).toBe(true);
		tracker.input(1000, 120);
		tracker.input(undefined, 120);
		tracker.input(0, 120);
		expect(tracker.reading(120)).toEqual({ ms: 5, stale: false, source: 'link' });
		expect(tracker.receive('sync:1:1105000:1105000', 121)).toBe(false);
		tracker.probe(200);
		expect(tracker.receive('sync:2:1200000:1190000', 210)).toBe(false);
		tracker.probe(300);
		expect(tracker.receive('sync:3:1300000:1300000', 2400)).toBe(false);
	});
	it('uses the fastest recent exchange and resets smoothing after inactivity', () => {
		const tracker = createLatencyTracker();
		tracker.probe(100);
		tracker.receive('sync:1:1105000:1105000', 110);
		tracker.probe(200);
		tracker.receive('sync:2:1240000:1240000', 250);
		tracker.input(1300, 320);
		expect(tracker.reading(320).ms).toBe(20);
		tracker.input(1400, 440);
		expect(tracker.reading(440).ms).toBe(24);
		tracker.input(5000, 4010);
		expect(tracker.reading(4010).ms).toBe(10);
		expect(createLatencyTracker().reading(4010).ms).toBeNull();
	});
});
