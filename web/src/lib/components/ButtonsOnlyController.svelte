<script lang="ts">
	import { stickOffset, type ControllerState } from '../controller';
	import DirectionArrow from './DirectionArrow.svelte';
	let { controller, number }: { controller: ControllerState; number: number } = $props();
	const uid = $props.id();
	const buttons = [
		{ id: 'L', label: 'L', color: '#a78bfa' },
		{ id: 'R', label: 'R', color: '#a78bfa' },
		{ id: 'Z', label: 'Z', color: '#a78bfa' },
		{ id: 'UP', label: 'D ↑', color: '#60d9ff' },
		{ id: 'DOWN', label: 'D ↓', color: '#60d9ff' },
		{ id: 'LEFT', label: 'D ←', color: '#60d9ff' },
		{ id: 'RIGHT', label: 'D →', color: '#60d9ff' },
		{ id: 'START', label: 'START', color: '#e3443e' },
		{ id: 'A', label: 'A', color: '#2865ed' },
		{ id: 'B', label: 'B', color: '#23ad52' },
		{ id: 'CUP', label: 'C ↑', color: '#f5ca30' },
		{ id: 'CDOWN', label: 'C ↓', color: '#f5ca30' },
		{ id: 'CLEFT', label: 'C ←', color: '#f5ca30' },
		{ id: 'CRIGHT', label: 'C →', color: '#f5ca30' }
	] as const;
	const positions = {
		L: [80, 25],
		R: [360, 25],
		UP: [80, 88],
		DOWN: [80, 152],
		LEFT: [48, 120],
		RIGHT: [112, 120],
		B: [245, 33],
		A: [245, 93],
		START: [185, 33],
		Z: [185, 93],
		CUP: [360, 88],
		CDOWN: [360, 152],
		CLEFT: [328, 120],
		CRIGHT: [392, 120]
	} as const;
	const dpad = new Set(['UP', 'DOWN', 'LEFT', 'RIGHT']);
	let pressed = $derived(
		buttons
			.filter(({ id }) => controller.buttons[id])
			.map(({ id }) => id)
			.join(', ') || 'none'
	);
</script>

<svg
	viewBox="0 0 440 200"
	role="img"
	aria-label={`Controller ${number}: pressed ${pressed}; stick X ${controller.x}, Y ${controller.y}`}
>
	<title>Player {number} — buttons only</title>
	<defs>
		<linearGradient id={`${uid}-dpad`} x1="0" y1="0" x2="0.3" y2="1">
			<stop stop-color="#888" /><stop offset="0.45" stop-color="#555" /><stop
				offset="1"
				stop-color="#333"
			/>
		</linearGradient>
	</defs>
	<g
		transform="translate(178 112) scale(0.65)"
		class="stick"
		class:active={controller.x !== 0 || controller.y !== 0}
	>
		<circle class="gate" cx="57" cy="70" r="43" />
		<path d="M20 70h74M57 33v74" />
		<circle
			class="thumb"
			cx={57 + stickOffset(controller.x) * 0.65}
			cy={70 - stickOffset(controller.y) * 0.65}
			r="16"
		/>
	</g>
	<g class="dpad-body">
		<path
			fill={`url(#${uid}-dpad)`}
			stroke="#999"
			stroke-width="2"
			d="M68 72h24q4 0 4 4v28h28q4 0 4 4v24q0 4-4 4H96v28q0 4-4 4H68q-4 0-4-4v-28H36q-4 0-4-4v-24q0-4 4-4h28V76q0-4 4-4z"
		/>
		<path class="bevel" d="M67 101V76h25v31h31v25M36 132v-25h28M68 139v24h24" />
		<circle cx="80" cy="120" r="5" fill="#444" />
	</g>
	{#each buttons as button}
		<g
			class="button"
			class:direction={dpad.has(button.id)}
			class:pressed={controller.buttons[button.id]}
			style:--color={button.color}
			transform={`translate(${positions[button.id][0]} ${positions[button.id][1]})`}
		>
			{#if dpad.has(button.id)}
				<rect x="-16" y="-16" width="32" height="32" rx="2" />
			{:else if button.id.startsWith('C')}
				<rect x="-16" y="-16" width="32" height="32" rx="16" />
			{:else if button.id === 'L' || button.id === 'R'}
				<rect x="-48" y="-15" width="96" height="30" rx="8" />
			{:else if button.id === 'Z'}
				<rect x="-15" y="-23" width="30" height="46" rx="6" />
			{:else}
				<rect x="-23" y="-23" width="46" height="46" rx="23" />
			{/if}
			{#if dpad.has(button.id) || button.id.startsWith('C')}
				<g class="arrow"><DirectionArrow direction={button.id} /></g>
			{:else}
				<text x="0" y="0" class:start={button.id === 'START'}>{button.label}</text>
			{/if}
		</g>
	{/each}
</svg>

<style>
	svg {
		display: block;
		width: 100%;
		height: auto;
	}
	.dpad-body {
		opacity: 0.4;
	}
	.bevel {
		fill: none;
		stroke: #bbb;
		stroke-width: 1.5;
		stroke-linejoin: round;
	}
	.button.direction:not(.pressed) rect {
		fill: transparent;
		stroke: none;
	}
	.arrow {
		fill: #eee;
	}
	.button {
		opacity: 0.4;
	}
	.button rect {
		fill: #656565;
		stroke: #999;
		stroke-width: 1.5;
	}
	text {
		fill: #eee;
		text-anchor: middle;
		dominant-baseline: central;
		font-family: inherit;
		font-size: 16px;
		font-weight: 700;
	}
	text.start {
		font-size: 10px;
	}
	.button.pressed {
		opacity: 1;
	}
	.button.pressed rect {
		fill: var(--color);
		stroke: var(--color);
		filter: drop-shadow(0 0 3px var(--color));
	}
	.stick {
		opacity: 0.4;
	}
	.gate {
		fill: #333;
		stroke: #999;
		stroke-width: 2;
	}
	.stick path {
		stroke: #777;
	}
	.thumb {
		fill: #bbb;
		stroke: #eee;
		stroke-width: 1.5;
	}
	.stick.active {
		opacity: 1;
	}
	.stick.active .thumb {
		fill: #60d9ff;
	}
</style>
