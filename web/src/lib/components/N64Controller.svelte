<script lang="ts">
	import { emptyState, stickOffset, type ControllerState } from '../controller';
	let { controller = emptyState(), number = 1 }: { controller?: ControllerState; number?: number } =
		$props();
	const uid = $props.id();
	const face = [
		{ id: 'B', x: 299, y: 170, r: 15, color: '#23ad52', label: 'B' },
		{ id: 'A', x: 329, y: 198, r: 16, color: '#2865ed', label: 'A' },
		{ id: 'CUP', x: 359, y: 119, r: 12, color: '#f5ca30', label: '▲' },
		{ id: 'CLEFT', x: 334, y: 143, r: 12, color: '#f5ca30', label: '◀' },
		{ id: 'CRIGHT', x: 384, y: 143, r: 12, color: '#f5ca30', label: '▶' },
		{ id: 'CDOWN', x: 359, y: 168, r: 12, color: '#f5ca30', label: '▼' },
		{ id: 'START', x: 220, y: 174, r: 14, color: '#e3443e', label: 'START' }
	] as const;
	const directions = [
		{ id: 'UP', d: 'M77 129h23v24H77z', arrow: 'M83 144l6-7 6 7z' },
		{ id: 'DOWN', d: 'M77 176h23v24H77z', arrow: 'M83 185l6 7 6-7z' },
		{ id: 'LEFT', d: 'M53 153h24v23H53z', arrow: 'M68 159l-7 6 7 6z' },
		{ id: 'RIGHT', d: 'M100 153h24v23h-24z', arrow: 'M109 159l7 6-7 6z' }
	] as const;
	let pressed = $derived(
		Object.entries(controller.buttons)
			.filter(([, down]) => down)
			.map(([name]) => name)
			.join(', ') || 'none'
	);
</script>

<svg
	viewBox="0 0 440 410"
	role="img"
	aria-label={`Controller ${number}: pressed ${pressed}; stick X ${controller.x}, Y ${controller.y}`}
>
	<title>N64 controller {number}</title>
	<defs>
		<linearGradient id={`${uid}-shell`} x1="0" y1="0" x2=".7" y2="1">
			<stop stop-color="#d0d0d0" /><stop offset=".45" stop-color="#b6b6b6" /><stop
				offset="1"
				stop-color="#929292"
			/>
		</linearGradient>
		<linearGradient id={`${uid}-face`} x1="0" y1="0" x2="0" y2="1">
			<stop stop-color="#c7c7c7" /><stop offset="1" stop-color="#aaa" />
		</linearGradient>
		<radialGradient id={`${uid}-grip`} cx=".45" cy=".2" r=".9">
			<stop stop-color="#d1d1d1" /><stop offset="1" stop-color="#969696" />
		</radialGradient>
		<radialGradient id={`${uid}-stick`} cx=".4" cy=".3">
			<stop stop-color="#e6e6e6" /><stop offset=".8" stop-color="#c9c9c9" /><stop
				offset="1"
				stop-color="#929292"
			/>
		</radialGradient>
	</defs>
	<!-- Shoulder buttons follow the upper edge of the two round side housings. -->
	<g class="neutral-button" class:pressed={controller.buttons.L}>
		<path d="M43 76Q69 58 132 53L149 65L48 94Z" />
		<text x="90" y="64">L</text>
	</g>
	<g class="neutral-button" class:pressed={controller.buttons.R}>
		<path d="M397 76Q371 58 308 53L291 65L392 94Z" />
		<text x="350" y="64">R</text>
	</g>
	<!-- The grips turn inward underneath a broad, rounded faceplate. -->
	<path
		class="shell"
		fill={`url(#${uid}-shell)`}
		d="M133 66Q137 44 169 40Q220 30 271 40Q303 44 307 66C370 66 415 87 422 139C425 163 423 190 427 223C434 267 428 309 416 330Q408 343 395 340C380 339 372 313 365 287L349 231C329 231 300 231 289 248C280 263 279 285 273 313C262 367 248 398 229 403Q220 406 211 403C192 398 178 367 167 313C161 285 160 263 151 248C140 231 111 231 91 231L75 287C68 313 60 339 45 340Q32 343 24 330C12 309 6 267 13 223C17 190 15 163 18 139C25 87 70 66 133 66Z"
	/>
	<path
		fill={`url(#${uid}-grip)`}
		d="M20 184C30 219 54 232 89 233L71 291Q57 344 39 332C20 318 13 246 20 184Z"
	/>
	<path
		fill={`url(#${uid}-grip)`}
		d="M420 184C410 219 386 232 351 233L369 291Q383 344 401 332C420 318 427 246 420 184Z"
	/>
	<path
		class="faceplate"
		fill={`url(#${uid}-face)`}
		d="M134 68C77 68 26 87 20 138C12 194 40 221 87 230L130 235Q154 239 162 263Q170 282 177 314Q192 379 211 398Q220 406 229 398Q248 379 263 314Q270 282 278 263Q286 239 310 235L353 230C400 221 428 194 420 138C414 87 363 68 306 68Q297 49 272 43Q220 31 168 43Q143 49 134 68Z"
	/>
	<path class="tower-edge" d="M133 68Q139 116 150 148M307 68Q301 116 290 148" />
	<path class="tower-light" d="M139 58Q220 28 301 58" />
	<rect class="logo-border" x="172" y="78" width="96" height="23" rx="11" />
	<text class="logo" x="220" y="90">Player {number}</text>
	<circle cx="89" cy="165" r="44" fill="#a1a1a1" stroke="#bdbdbd" stroke-width="2" />
	<path
		class="dpad"
		d="M80 128h17q4 0 4 4v20h20q4 0 4 4v17q0 4-4 4h-20v20q0 4-4 4H80q-4 0-4-4v-20H56q-4 0-4-4v-17q0-4 4-4h20v-20q0-4 4-4z"
	/>
	{#each directions as direction}
		<g class="direction" class:pressed={controller.buttons[direction.id]}>
			<path class="press-surface" d={direction.d} />
			<path class="arrow" d={direction.arrow} />
		</g>
	{/each}
	<circle cx="89" cy="165" r="5" fill="#505050" />
	<path
		d="M336 117Q359 94 382 117L402 137Q407 143 401 150L380 173Q359 194 338 173L317 150Q311 143 317 137Z"
		fill="#a0a0a0"
		stroke="#bfbfbf"
	/>
	{#each face as button}
		<g
			class="face-button"
			class:c-button={button.id.startsWith('C')}
			class:pressed={controller.buttons[button.id]}
			style:--button-color={button.color}
		>
			<circle class="socket" cx={button.x} cy={button.y + 1} r={button.r + 2} />
			<circle class="cap" cx={button.x} cy={button.y} r={button.r} />
			<path
				class="cap-highlight"
				d={`M${button.x - button.r * 0.7} ${button.y - button.r * 0.3}Q${button.x - button.r * 0.2} ${button.y - button.r} ${button.x + button.r * 0.5} ${button.y - button.r * 0.65}`}
			/>
			<text x={button.x} y={button.y + 1} class:start={button.id === 'START'}>{button.label}</text>
		</g>
	{/each}
	<!-- Round recessed stick housing with an octagonal gate. -->
	<circle cx="220" cy="258" r="44" fill="#4d4d4d" stroke="#999" stroke-width="2" />
	<circle cx="220" cy="258" r="39" fill="#595959" stroke="#666" />
	<path
		d="M208 230h24l17 17v23l-17 17h-24l-17-17v-23z"
		fill="#383838"
		stroke="#777"
		stroke-width="2"
	/>
	<g
		transform={`translate(${stickOffset(controller.x) * 0.42}, ${-stickOffset(controller.y) * 0.42})`}
	>
		<path d="M208 257l3 16q9 7 18 0l3-16" fill="#aaa" />
		<circle cx="220" cy="255" r="19" fill={`url(#${uid}-stick)`} stroke="#aaa" />
		{#each [5, 9, 13, 16] as radius}<circle
				cx="220"
				cy="255"
				r={radius}
				class="stick-ring"
			/>{/each}
	</g>
	<!-- Z is on the back. A separate callout shows it without an incorrect button on the front. -->
	<path d="M251 320l34 32h19" class="rear-line" />
	<g class="neutral-button rear" class:pressed={controller.buttons.Z}>
		<rect x="307" y="340" width="32" height="23" rx="7" />
		<text x="323" y="352">Z</text>
	</g>
	<text class="rear-label" x="363" y="352">REAR</text>
</svg>

<style>
	svg {
		display: block;
		width: 100%;
		height: auto;
		max-height: 380px;
		overflow: visible;
	}
	text {
		text-anchor: middle;
		dominant-baseline: middle;
		font-family: inherit;
		font-weight: 700;
		font-size: 12px;
		fill: #e2e2e2;
		pointer-events: none;
	}
	.shell {
		stroke: #838383;
		stroke-width: 2;
		stroke-linejoin: round;
	}
	.faceplate {
		stroke: #bdbdbd;
		stroke-width: 1.5;
	}
	.tower-edge {
		fill: none;
		stroke: #9b9b9b;
		stroke-width: 2;
		opacity: 0.65;
	}
	.tower-light {
		fill: none;
		stroke: #e0e0e0;
		stroke-width: 2;
		opacity: 0.65;
	}
	.logo-border {
		fill: #b3b3b3;
		stroke: #939393;
		stroke-width: 1.5;
	}
	.logo {
		fill: #7a7a7a;
		font-size: 16px;
		font-weight: 800;
		letter-spacing: -0.5px;
		paint-order: stroke;
		stroke: #d1d1d1;
		stroke-width: 0.5;
	}
	.neutral-button path,
	.neutral-button rect {
		fill: #656565;
		stroke: #444;
		stroke-width: 2;
	}
	.neutral-button text {
		font-size: 10px;
	}
	.neutral-button.pressed path,
	.neutral-button.pressed rect {
		fill: #d4d4d4;
		stroke: #eee;
		filter: drop-shadow(0 0 3px #ddd8);
	}
	.neutral-button.pressed text {
		fill: #333;
	}
	.dpad {
		fill: #484848;
		stroke: #303030;
		stroke-width: 3;
	}
	.press-surface {
		fill: transparent;
	}
	.arrow {
		fill: #616161;
	}
	.direction.pressed .press-surface {
		fill: #acacac;
		stroke: #e1e1e1;
		stroke-width: 1;
	}
	.direction.pressed .arrow {
		fill: #393939;
	}
	.socket {
		fill: #777;
		stroke: #d1d1d1;
		stroke-width: 1;
	}
	.cap {
		fill: #737373;
		stroke: #505050;
		stroke-width: 1.5;
	}
	.cap-highlight {
		fill: none;
		stroke: #aaa;
		stroke-width: 1;
		stroke-linecap: round;
	}
	.face-button .start {
		font-size: 5px;
		letter-spacing: 0.1px;
	}
	.face-button.pressed .cap {
		fill: var(--button-color);
		stroke: var(--button-color);
		filter: drop-shadow(0 0 4px var(--button-color));
	}
	.face-button.pressed .cap-highlight {
		stroke: #ffffff80;
	}
	.face-button.pressed text {
		fill: #fff;
	}
	.face-button.c-button.pressed text {
		fill: #453800;
	}
	.stick-ring {
		fill: none;
		stroke: #999;
		stroke-width: 0.8;
	}
	.rear-line {
		fill: none;
		stroke: #808080;
		stroke-width: 1;
		stroke-dasharray: 3 3;
	}
	.rear-label {
		fill: #aaa;
		font-size: 8px;
		font-weight: 500;
		letter-spacing: 1px;
	}
</style>
