<script lang="ts">
	import { onMount } from 'svelte';
	import { decodeFrame, emptyState, createFrameBuffer } from '$lib/controller';
	import ControllerDashboard from '$lib/components/ControllerDashboard.svelte';

	let controllers = $state(Array.from({ length: 4 }, emptyState));
	let received = $state([false, false, false, false]);
	let connection = $state('connecting…');
	let connected = $state(false);

	onMount(() => {
		let ws: WebSocket | null = null;
		let reconnectTimer: ReturnType<typeof setTimeout> | undefined;
		let animationFrame: number | undefined;
		const pending = createFrameBuffer();
		let disposed = false;

		function connect() {
			const protocol = location.protocol === 'https:' ? 'wss:' : 'ws:';
			ws = new WebSocket(`${protocol}//${location.host}/ws`);
			ws.binaryType = 'arraybuffer';
			ws.onopen = () => {
				connection = 'connected';
				connected = true;
			};
			ws.onclose = (event) => {
				if (disposed) return;
				connection = `disconnected (${event.code}) — retrying…`;
				connected = false;
				ws = null;
				reconnectTimer = setTimeout(connect, 1000);
			};
			ws.onerror = (event) => console.log('[ws] error', event);
			ws.onmessage = (event) => {
				if (!(event.data instanceof ArrayBuffer)) return;
				const frame = decodeFrame(new Uint8Array(event.data));
				if (!frame) return;
				pending.push(frame);
				if (animationFrame !== undefined) return;
				animationFrame = requestAnimationFrame(() => {
					animationFrame = undefined;
					for (const [index, frame] of pending.drain()) {
						controllers[index] = frame;
						received[index] = true;
					}
				});
			};
		}

		function dispose() {
			disposed = true;
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

<ControllerDashboard {controllers} {received} {connection} {connected} />
