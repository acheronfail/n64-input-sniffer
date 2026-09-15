import { afterEach, beforeEach, expect, it, vi } from 'vitest';
import { startHeartbeat } from './heartbeat';

beforeEach(() => vi.useFakeTimers({ toFake: ['setInterval', 'clearInterval', 'performance'] }));
afterEach(() => vi.useRealTimers());

it('detects a silent power loss and stops sending', () => {
	const send = vi.fn();
	const timeout = vi.fn();
	startHeartbeat(send, timeout);
	vi.advanceTimersByTime(2999);
	expect(timeout).not.toHaveBeenCalled();
	vi.advanceTimersByTime(1);
	expect(timeout).toHaveBeenCalledOnce();
	expect(send).toHaveBeenCalledTimes(2);
	vi.advanceTimersByTime(10000);
	expect(timeout).toHaveBeenCalledOnce();
	expect(send).toHaveBeenCalledTimes(2);
});

it('keeps an idle device connected while replies arrive', () => {
	const timeout = vi.fn();
	const heartbeat = startHeartbeat(vi.fn(), timeout);
	for (let second = 0; second < 60; second++) {
		vi.advanceTimersByTime(1000);
		heartbeat.received();
	}
	expect(timeout).not.toHaveBeenCalled();
	vi.advanceTimersByTime(3000);
	expect(timeout).toHaveBeenCalledOnce();
});

it('cancels checks when the page or socket closes', () => {
	const send = vi.fn();
	const timeout = vi.fn();
	const heartbeat = startHeartbeat(send, timeout);
	heartbeat.stop();
	vi.advanceTimersByTime(10000);
	expect(send).not.toHaveBeenCalled();
	expect(timeout).not.toHaveBeenCalled();
});

it('skips heartbeats during controller traffic and resumes after traffic stops', () => {
	const send = vi.fn();
	const timeout = vi.fn();
	const heartbeat = startHeartbeat(send, timeout);
	for (let frame = 0; frame < 120; frame++) {
		vi.advanceTimersByTime(500);
		heartbeat.received();
	}
	expect(send).not.toHaveBeenCalled();
	expect(timeout).not.toHaveBeenCalled();
	vi.advanceTimersByTime(1000);
	expect(send).toHaveBeenCalledOnce();
	vi.advanceTimersByTime(1000);
	heartbeat.received();
	vi.advanceTimersByTime(2000);
	expect(timeout).not.toHaveBeenCalled();
	vi.advanceTimersByTime(1000);
	expect(timeout).toHaveBeenCalledOnce();
});
