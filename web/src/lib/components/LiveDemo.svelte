<script lang="ts">
	import { onMount } from 'svelte';
	import { decodeFrame, emptyState } from '../controller';
	import ControllerDashboard from './ControllerDashboard.svelte';
	let controllers = $state(Array.from({ length: 4 }, emptyState));
	onMount(() => {
		let tick = 0;
		const timer = setInterval(() => {
			tick++;
			controllers = controllers.map((_, index) => {
				const phase = tick / 18 + (index * Math.PI) / 2;
				const button = Math.floor(tick / 8 + index) % 14;
				return decodeFrame(
					new Uint8Array([
						index,
						button < 8 ? 1 << button : 0,
						button >= 8 ? 1 << (button - 8) : 0,
						Math.round(Math.cos(phase) * 90),
						Math.round(Math.sin(phase) * 90)
					])
				)!;
			});
		}, 50);
		return () => clearInterval(timer);
	});
</script>

<ControllerDashboard
	{controllers}
	received={[true, true, true, true]}
	connected
	connection="Simulated inputs"
	persistSettings={false}
/>
