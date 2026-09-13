<script lang="ts">
	import { onMount } from 'svelte';
	import { decodeFrame, emptyState, stickOffset } from '$lib/controller';

	let controller = $state(emptyState());
	let connection = $state('connecting…');
	let connected = $state(false);
	let disconnected = $state(false);

	onMount(() => {
		let ws: WebSocket | null = null;
		let reconnectTimer: ReturnType<typeof setTimeout> | undefined;
		let animationFrame: number | undefined;
		let latest: ReturnType<typeof decodeFrame> = null;
		let disposed = false;

		function connect() {
			const protocol = location.protocol === 'https:' ? 'wss:' : 'ws:';
			ws = new WebSocket(`${protocol}//${location.host}/ws`);
			ws.binaryType = 'arraybuffer';
			ws.onopen = () => {
				connection = 'connected';
				connected = true;
				disconnected = false;
			};
			ws.onclose = (event) => {
				if (disposed) return;
				connection = `disconnected (${event.code}) — retrying…`;
				connected = false;
				disconnected = true;
				ws = null;
				reconnectTimer = setTimeout(connect, 1000);
			};
			ws.onerror = (event) => console.log('[ws] error', event);
			ws.onmessage = (event) => {
				if (!(event.data instanceof ArrayBuffer)) return;
				const frame = decodeFrame(new Uint8Array(event.data));
				if (!frame) return;
				latest = frame;
				if (animationFrame !== undefined) return;
				animationFrame = requestAnimationFrame(() => {
					animationFrame = undefined;
					if (!latest) return;
					// Legacy four-byte frames leave the last known pad label intact.
					controller = { ...latest, padIndex: latest.padIndex ?? controller.padIndex };
					latest = null;
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

<div class="wrap">
	<h1>N64 SPY</h1>
	<div id="conn" class:up={connected} class:down={disconnected}>{connection}</div>
	<div id="pad">pad: {controller.padIndex === null ? '--' : controller.padIndex + 1}</div>

	<div class="pad">
		<!-- Left column: shoulders, D-pad -->
		<div class="col">
			<div id="L" class="btn wide grey" class:on={controller.buttons.L}>L</div>
			<div class="dpad">
				<div id="UP" class="btn small grey up" class:on={controller.buttons.UP}></div>
				<div id="LEFT" class="btn small grey left" class:on={controller.buttons.LEFT}></div>
				<div id="RIGHT" class="btn small grey right" class:on={controller.buttons.RIGHT}></div>
				<div id="DOWN" class="btn small grey down" class:on={controller.buttons.DOWN}></div>
			</div>
		</div>

		<!-- Center column: Start, Z, analog stick -->
		<div class="col">
			<div id="START" class="btn wide grey" class:on={controller.buttons.START}>START</div>
			<div id="Z" class="btn wide grey" class:on={controller.buttons.Z}>Z</div>
			<div class="stick">
				<div
					id="dot"
					class="dot"
					style:transform={`translate(${stickOffset(controller.x)}px, ${-stickOffset(controller.y)}px)`}
				></div>
			</div>
			<div class="axis">
				x:<span id="sx">{controller.x}</span> y:<span id="sy">{controller.y}</span>
			</div>
		</div>

		<!-- Right column: shoulder, A/B, C cluster -->
		<div class="col">
			<div id="R" class="btn wide grey" class:on={controller.buttons.R}>R</div>
			<div class="ab">
				<div id="B" class="btn round green" class:on={controller.buttons.B}>B</div>
				<div id="A" class="btn round blue" class:on={controller.buttons.A}>A</div>
			</div>
			<div class="cpad">
				<div id="CUP" class="btn small yellow cu" class:on={controller.buttons.CUP}>C&#9650;</div>
				<div id="CLEFT" class="btn small yellow cl" class:on={controller.buttons.CLEFT}>
					C&#9664;
				</div>
				<div id="CRIGHT" class="btn small yellow cr" class:on={controller.buttons.CRIGHT}>
					C&#9654;
				</div>
				<div id="CDOWN" class="btn small yellow cd" class:on={controller.buttons.CDOWN}>
					C&#9660;
				</div>
			</div>
		</div>
	</div>
</div>
