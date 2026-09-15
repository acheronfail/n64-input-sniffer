export type LatencyReading = { ms: number | null; stale: boolean; source?: 'input' | 'link' };
type Sample = { at: number; offset: number; rtt: number };

export function createLatencyTracker() {
	let samples: Sample[] = [];
	let pending: { id: number; sent: number } | undefined;
	let sequence = 0;
	let firstEspTime: number | undefined;
	let ms: number | null = null;
	let lastInput = -Infinity;
	let linkMs: number | null = null;
	let lastReply = -Infinity;
	function best(now: number) {
		samples = samples.filter((sample) => now - sample.at < 30000);
		return samples.reduce<Sample | undefined>(
			(best, sample) => (!best || sample.rtt < best.rtt ? sample : best),
			undefined
		);
	}
	return {
		probe(now: number): string {
			pending = { id: ++sequence, sent: now };
			return `sync:${sequence}`;
		},
		receive(message: string, now: number): boolean {
			const match = /^sync:(\d{1,10}):(\d{1,16}):(\d{1,16})$/.exec(message);
			if (!match || !pending || Number(match[1]) !== pending.id) return false;
			const { sent } = pending;
			pending = undefined;
			const receivedUs = Number(match[2]);
			const repliedUs = Number(match[3]);
			if (!Number.isSafeInteger(receivedUs) || !Number.isSafeInteger(repliedUs)) return false;
			const received = receivedUs / 1000;
			const replied = repliedUs / 1000;
			const rtt = now - sent - (replied - received);
			if (replied < received || rtt < 0 || now - sent > 2000 || now < sent) return false;
			best(now);
			samples.push({ at: now, rtt, offset: (received - sent + (replied - now)) / 2 });
			firstEspTime ??= received;
			const sample = best(now)!;
			const delay = Math.max(0, now - replied + sample.offset);
			linkMs = linkMs === null || now - lastReply > 3000 ? delay : linkMs * 0.8 + delay * 0.2;
			lastReply = now;
			return true;
		},
		input(decodedMs: number | undefined, now: number) {
			const sample = best(now);
			if (!sample || !decodedMs || firstEspTime === undefined || decodedMs < firstEspTime) return;
			const delay = now - decodedMs + sample.offset;
			// Small negative estimates can result from unequal network delays.
			if (!Number.isFinite(delay) || delay < -sample.rtt / 2) return;
			const value = Math.max(0, delay);
			ms = ms === null || now - lastInput > 3000 ? value : ms * 0.8 + value * 0.2;
			lastInput = now;
		},
		reading(now: number): LatencyReading {
			const synced = !!best(now);
			if (ms !== null && now - lastInput <= 3000) {
				return { ms: synced ? ms : null, stale: !synced, source: 'input' };
			}
			return {
				ms: synced ? linkMs : null,
				stale: !synced || now - lastReply > 3000,
				source: 'link'
			};
		}
	};
}
