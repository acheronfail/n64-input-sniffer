<script lang="ts">
	import { onMount } from 'svelte';
	import { startHeartbeat } from '$lib/heartbeat';
	import { decodeFrame, emptyState, createFrameBuffer } from '$lib/controller';
	import ControllerDashboard from '$lib/components/ControllerDashboard.svelte';

	let controllers = $state(Array.from({ length: 4 }, emptyState));
	let connection = $state('connecting…');
	let connected = $state(false);

	onMount(() => {
		let ws: WebSocket | null = null;
		let reconnectTimer: ReturnType<typeof setTimeout> | undefined;
		let animationFrame: number | undefined;
		let heartbeat: ReturnType<typeof startHeartbeat> | undefined;
		let connectTimer: ReturnType<typeof setTimeout> | undefined;
		const pending = createFrameBuffer();
		let disposed = false;

		function disconnect(status: string) {
			if (disposed) return;
			heartbeat?.stop();
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
				if (event.data === 'pong') {
					heartbeat?.received();
					return;
				}
				if (!(event.data instanceof ArrayBuffer)) return;
				const frame = decodeFrame(new Uint8Array(event.data));
				if (!frame) return;
				heartbeat?.received();
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

<ControllerDashboard {controllers} {connection} {connected} />
