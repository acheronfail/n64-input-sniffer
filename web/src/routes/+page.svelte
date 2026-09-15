<script lang="ts">
	import { onMount } from 'svelte';
	import { startHeartbeat } from '$lib/heartbeat';
	import { createLatencyTracker, type LatencyReading } from '$lib/latency';
	import { decodeFrame, emptyState, createFrameBuffer } from '$lib/controller';
	import ControllerDashboard from '$lib/components/ControllerDashboard.svelte';

	let controllers = $state(Array.from({ length: 4 }, emptyState));
	let connection = $state('connecting…');
	let connected = $state(false);
	let latency = $state<LatencyReading>({ ms: null, stale: true });

	onMount(() => {
		let ws: WebSocket | null = null;
		let reconnectTimer: ReturnType<typeof setTimeout> | undefined;
		let animationFrame: number | undefined;
		let heartbeat: ReturnType<typeof startHeartbeat> | undefined;
		let connectTimer: ReturnType<typeof setTimeout> | undefined;
		const pending = createFrameBuffer();
		let tracker = createLatencyTracker();
		let latencyTimer: ReturnType<typeof setInterval> | undefined;
		let disposed = false;

		function disconnect(status: string) {
			if (disposed) return;
			heartbeat?.stop();
			clearInterval(latencyTimer);
			latency = { ms: null, stale: true };
			clearTimeout(connectTimer);
			connection = status;
			connected = false;
			if (ws) {
				ws.onopen = ws.onclose = ws.onerror = ws.onmessage = null;
				ws.close();
				ws = null;
			}
			reconnectTimer = setTimeout(connect, 1000);
		}

		function connect() {
			const protocol = location.protocol === 'https:' ? 'wss:' : 'ws:';
			ws = new WebSocket(`${protocol}//${location.host}/ws`);
			ws.binaryType = 'arraybuffer';
			connectTimer = setTimeout(() => disconnect('connection timed out — retrying…'), 3000);
			ws.onopen = () => {
				clearTimeout(connectTimer);
				connection = 'connected';
				connected = true;
				tracker = createLatencyTracker();
				const probe = () => {
					ws?.send(tracker.probe(performance.now()));
					latency = tracker.reading(performance.now());
				};
				probe();
				latencyTimer = setInterval(probe, 1000);
				heartbeat = startHeartbeat(
					() => ws?.send('ping'),
					() => disconnect('connection lost — retrying…')
				);
			};
			ws.onclose = (event) => {
				disconnect(`disconnected (${event.code}) — retrying…`);
			};
			ws.onerror = (event) => console.log('[ws] error', event);
			ws.onmessage = (event) => {
				const receivedAt = performance.now();
				if (typeof event.data === 'string' && tracker.receive(event.data, receivedAt)) {
					heartbeat?.received();
					return;
				}
				if (event.data === 'pong') {
					heartbeat?.received();
					return;
				}
				if (!(event.data instanceof ArrayBuffer)) return;
				const frame = decodeFrame(new Uint8Array(event.data));
				if (!frame) return;
				heartbeat?.received();
				tracker.input(frame.decodedMs, receivedAt);
				pending.push(frame);
				if (animationFrame !== undefined) return;
				animationFrame = requestAnimationFrame(() => {
					animationFrame = undefined;
					for (const [index, frame] of pending.drain()) {
						controllers[index] = frame;
					}
				});
			};
		}

		function dispose() {
			disposed = true;
			heartbeat?.stop();
			clearInterval(latencyTimer);
			latency = { ms: null, stale: true };
			clearTimeout(connectTimer);
			clearTimeout(reconnectTimer);
			if (animationFrame !== undefined) cancelAnimationFrame(animationFrame);
			if (ws) {
				ws.onopen = ws.onclose = ws.onerror = ws.onmessage = null;
				ws.close(1000, 'page unload');
			}
		}

		connect();
		window.addEventListener('beforeunload', dispose);
		return () => {
			window.removeEventListener('beforeunload', dispose);
			dispose();
		};
	});
</script>

<svelte:head>
	<title>N64 Spy</title>
	<link rel="icon" href="data:," />
</svelte:head>

<ControllerDashboard {controllers} {connection} {connected} {latency} />
