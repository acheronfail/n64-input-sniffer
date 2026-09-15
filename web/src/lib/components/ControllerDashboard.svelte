<script lang="ts">
	import { onMount, untrack, tick } from 'svelte';
	import { emptyState, type ControllerState } from '../controller';
	import {
		ALL_CONTROLLERS,
		parseVisibility,
		SETTINGS_KEY,
		MINIMAL_KEY,
		MINIMAL_CONNECTION_KEY,
		MINIMAL_LATENCY_KEY,
		BACKGROUND_KEY,
		DEFAULT_BACKGROUND,
		DEFAULT_BACKGROUND_COLOR
	} from '../settings';
	import N64Controller from './N64Controller.svelte';
	import type { LatencyReading } from '../latency';
	let {
		controllers = Array.from({ length: 4 }, emptyState),
		connection = 'connecting…',
		connected = false,
		latency = { ms: null, stale: true },
		initialVisible = ALL_CONTROLLERS,
		initialMinimal = false,
		initialBackground = DEFAULT_BACKGROUND,
		persistSettings = true
	}: {
		controllers?: ControllerState[];
		connection?: string;
		connected?: boolean;
		latency?: LatencyReading;
		initialVisible?: number[];
		initialMinimal?: boolean;
		initialBackground?: string;
		persistSettings?: boolean;
	} = $props();
	let visible = $state<number[]>(untrack(() => [...initialVisible]));
	let storageMessage = $state('');
	const inputId = $props.id();
	let background = $state(untrack(() => initialBackground));
	let backgroundColor = $state(
		untrack(() =>
			initialBackground === 'transparent' ? DEFAULT_BACKGROUND_COLOR : initialBackground
		)
	);
	let backgroundInput = $state(untrack(() => backgroundColor));
	let backgroundError = $state(false);
	function validColor(value: unknown): value is string {
		return (
			typeof value === 'string' &&
			CSS.supports('color', value) &&
			!/^(inherit|initial|unset|revert|revert-layer|currentcolor)$/i.test(value.trim()) &&
			!/\b(var|env)\(/i.test(value)
		);
	}
	function setBackground(value: string) {
		backgroundInput = value;
		backgroundError = !validColor(value) || value.trim().toLowerCase() === 'transparent';
		if (!backgroundError) {
			backgroundColor = background = value.trim();
			save(BACKGROUND_KEY, background);
		}
	}
	function setTransparent(value: boolean) {
		background = value ? 'transparent' : backgroundColor;
		backgroundInput = backgroundColor;
		backgroundError = false;
		save(BACKGROUND_KEY, background);
	}
	let minimal = $state(untrack(() => initialMinimal));
	let showMinimalConnection = $state(true);
	let showMinimalLatency = $state(false);
	let exitButton = $state<HTMLButtonElement>();
	let settingsSummary = $state<HTMLElement>();
	// Initialize from props. Keep the user's selection independent of incoming frames.
	onMount(() => {
		visible = [...initialVisible];
		if (persistSettings) {
			try {
				visible = parseVisibility(localStorage.getItem(SETTINGS_KEY));
				minimal = localStorage.getItem(MINIMAL_KEY) === 'true';
				showMinimalConnection = localStorage.getItem(MINIMAL_CONNECTION_KEY) !== 'false';
				showMinimalLatency = localStorage.getItem(MINIMAL_LATENCY_KEY) === 'true';
				const savedBackground = localStorage.getItem(BACKGROUND_KEY);
				// A malformed color preference must not prevent the other settings from loading.
				try {
					const value: unknown = savedBackground === null ? null : JSON.parse(savedBackground);
					if (validColor(value)) {
						background = value.trim().toLowerCase() === 'transparent' ? 'transparent' : value;
						if (background !== 'transparent') backgroundColor = backgroundInput = background;
					}
				} catch {
					/* Use the default background. */
				}
			} catch {
				storageMessage = 'Browser storage unavailable. Settings apply for this visit.';
			}
		}
	});
	function save(key: string, value: unknown) {
		if (persistSettings) {
			try {
				localStorage.setItem(key, JSON.stringify(value));
				storageMessage = '';
			} catch {
				storageMessage = 'Could not save settings. Settings apply for this visit.';
			}
		}
	}
	function select(indices: number[]) {
		visible = indices;
		save(SETTINGS_KEY, visible);
	}
	async function setMinimal(value: boolean) {
		minimal = value;
		save(MINIMAL_KEY, value);
		await tick();
		(value ? exitButton : settingsSummary)?.focus({ preventScroll: true });
	}
</script>

<svelte:window
	onkeydown={(event) => {
		if (minimal && event.key === 'Escape') {
			event.preventDefault();
			void setMinimal(false);
		}
	}}
/>

<div class="surface" style:background-color={background}>
	<main class="dashboard" class:minimal>
		{#if minimal}
			<button
				class="exit-minimal"
				bind:this={exitButton}
				onclick={() => setMinimal(false)}
				aria-label="Exit minimal mode"
				title="Exit minimal mode (Esc)"
			>
				<svg
					width="16"
					height="16"
					viewBox="0 0 24 24"
					fill="none"
					stroke="currentColor"
					stroke-width="1.5"
					aria-hidden="true"
				>
					<path d="M4 4h16v16H4zM4 9h16M9 9v11" />
				</svg>
			</button>
		{/if}
		<header>
			<div class="brand">
				<span class="brand-mark" aria-hidden="true">N</span>
				<div>
					<h1>N64 SPY</h1>
					<p>CONTROLLER INPUTS</p>
				</div>
			</div>
			<details class="settings">
				<summary bind:this={settingsSummary}>Settings</summary>
				<div class="settings-panel">
					<fieldset>
						<legend>Visible controllers</legend>
						<div class="choices">
							{#each ALL_CONTROLLERS as index}
								<label
									><input
										type="checkbox"
										checked={visible.includes(index)}
										onchange={(event) =>
											select(
												event.currentTarget.checked
													? [...visible, index].sort()
													: visible.filter((id) => id !== index)
											)}
									/>{index + 1}</label
								>
							{/each}
						</div>
					</fieldset>
					<div class="presets">
						<button onclick={() => select([...ALL_CONTROLLERS])}>Show all</button><button
							onclick={() => select([0])}>Only 1</button
						>
					</div>
					<button class="minimal-option" onclick={() => setMinimal(true)}
						>Enter minimal interface</button
					>
					<p>Controllers only. Use the corner button or Esc to exit.</p>
					<label class="indicator-option">
						<input
							type="checkbox"
							checked={showMinimalConnection}
							onchange={(event) => {
								showMinimalConnection = event.currentTarget.checked;
								save(MINIMAL_CONNECTION_KEY, showMinimalConnection);
							}}
						/>
						Show connection dot in minimal mode
					</label>
					<label class="indicator-option">
						<input
							type="checkbox"
							checked={showMinimalLatency}
							onchange={(event) => {
								showMinimalLatency = event.currentTarget.checked;
								save(MINIMAL_LATENCY_KEY, showMinimalLatency);
							}}
						/>
						Show latency in minimal mode
					</label>
					<fieldset class="background-options">
						<legend>Background</legend>
						<div class="choices">
							<label
								><input
									type="radio"
									name={`${inputId}-background-mode`}
									checked={background === 'transparent'}
									onchange={() => setTransparent(true)}
								/> Transparent</label
							>
							<label
								><input
									type="radio"
									name={`${inputId}-background-mode`}
									checked={background !== 'transparent'}
									onchange={() => setTransparent(false)}
								/> Color</label
							>
						</div>
					</fieldset>
					<label class="background-label" for={`${inputId}-background`}
						>Background color (CSS)</label
					>
					<div class="background-input">
						<input
							id={`${inputId}-background`}
							type="text"
							disabled={background === 'transparent'}
							value={backgroundInput}
							oninput={(event) => setBackground(event.currentTarget.value)}
							spellcheck="false"
							autocomplete="off"
							aria-invalid={backgroundError}
							aria-describedby={`${inputId}-background-help`}
						/>
						<button onclick={() => setTransparent(true)}>Reset</button>
					</div>
					<p id={`${inputId}-background-help`} class:color-error={backgroundError} role="status">
						{backgroundError
							? 'Enter a CSS color or select Transparent. The last valid color still applies.'
							: 'Use Transparent for OBS, or select Color for a chroma key background.'}
					</p>
					<p>{persistSettings ? 'Saved in this browser.' : 'Demo settings — not saved.'}</p>
					{#if storageMessage}<p role="status">{storageMessage}</p>{/if}
				</div>
			</details>
		</header>
		{#if !minimal || showMinimalConnection || showMinimalLatency}
			<div class="connection" class:connected role="status">
				{#if !minimal || showMinimalConnection}
					<span class="status-dot" role="img" aria-label={connection} title={connection}></span>
				{/if}
				{#if !minimal}{connection}{/if}
				{#if (minimal && showMinimalLatency) || (!minimal && connected)}
					<span
						class="latency"
						title={latency.source === 'link'
							? 'Estimated time from ESP clock reply to browser receipt. Excludes input queue and screen display delay. Unequal network delays affect accuracy.'
							: 'Estimated time from ESP decode to browser receipt. Excludes screen display delay. Unequal network delays affect accuracy.'}
					>
						{latency.source === 'link' ? 'Link latency' : 'Input latency'}: {!connected ||
						latency.ms === null
							? '—'
							: `≈${Math.round(latency.ms)} ms`}{connected && latency.ms !== null && latency.stale
							? ' (stale)'
							: ''}
					</span>
				{/if}
			</div>
		{/if}
		<section class="controllers" aria-label="Controller inputs">
			{#each ALL_CONTROLLERS.filter((index) => visible.includes(index)) as index (index)}
				{@const controller = controllers[index] ?? emptyState()}
				<article class="controller-card" aria-label={`Controller ${index + 1}`}>
					<div class="card-heading">
						<h2 aria-label={`Player ${index + 1}`}><span class="port">{index + 1}</span></h2>
					</div>
					<N64Controller {controller} number={index + 1} />
					<footer>
						<span>ANALOG STICK</span>
						<div><span>X <b>{controller.x}</b></span><span>Y <b>{controller.y}</b></span></div>
					</footer>
				</article>
			{/each}
		</section>
		{#if visible.length === 0}<p class="empty">
				No controllers selected. Open Settings to show a controller.
			</p>{/if}
	</main>
</div>

<style>
	.surface {
		min-height: 100vh;
		min-height: 100dvh;
		width: 100%;
	}
	.background-label {
		display: block;
		margin-top: 16px;
		margin-bottom: 7px;
	}
	.background-options {
		margin-top: 16px;
	}
	.background-options legend {
		margin-bottom: 0;
	}
	.background-input input:disabled {
		opacity: 0.5;
	}
	.background-input {
		display: flex;
		gap: 6px;
	}
	.background-input input {
		min-width: 0;
		width: 100%;
		height: auto;
		padding: 7px;
		border: 1px solid #526171;
		border-radius: 6px;
		color: #e4eaf1;
		background: #101720;
		font: inherit;
	}
	.background-input input[aria-invalid='true'] {
		border-color: #ffa4a4;
	}
	.settings-panel .color-error {
		color: #ffa4a4;
	}

	.dashboard {
		width: 100%;
		max-width: 1440px;
		margin: auto;
		padding: clamp(10px, 2.5vw, 32px);
	}
	header {
		display: flex;
		justify-content: space-between;
		align-items: center;
		gap: 12px;
		flex-wrap: wrap;
	}
	.brand {
		display: flex;
		align-items: center;
		gap: 10px;
	}
	.brand-mark {
		display: grid;
		place-items: center;
		width: 32px;
		height: 36px;
		border: 1px solid #4f655f;
		border-radius: 7px;
		font-size: 23px;
		font-weight: 900;
		color: #94e0b4;
	}
	h1 {
		font-size: 15px;
		letter-spacing: 0.16em;
		margin: 0;
	}
	.brand p {
		margin: 3px 0 0;
		font-size: 9px;
		letter-spacing: 0.14em;
		color: #96a3b3;
	}
	.settings {
		position: relative;
		font-size: 12px;
	}
	summary {
		cursor: pointer;
		padding: 8px 11px;
		border: 1px solid #35414e;
		border-radius: 7px;
	}
	.settings-panel {
		position: absolute;
		z-index: 2;
		right: 0;
		top: 44px;
		width: min(260px, calc(100vw - 20px));
		padding: 16px;
		border: 1px solid #455361;
		border-radius: 10px;
		background: #202a35;
		box-shadow: 0 12px 28px #0008;
	}
	fieldset {
		margin: 0;
		padding: 0;
		border: 0;
	}
	legend {
		margin-bottom: 12px;
		font-weight: 600;
	}
	.choices,
	.presets {
		display: flex;
		gap: 8px;
	}
	.choices label {
		display: flex;
		gap: 5px;
		align-items: center;
		padding: 8px 4px;
		cursor: pointer;
	}
	input {
		accent-color: #8dd9af;
		width: 16px;
		height: 16px;
	}
	button {
		background: #303e4c;
		border: 1px solid #526171;
		border-radius: 6px;
		padding: 7px 10px;
		color: inherit;
		font: inherit;
		cursor: pointer;
	}
	.settings-panel p {
		color: #b3bfcb;
		font-size: 11px;
		margin: 12px 0 0;
	}
	.connection {
		display: flex;
		flex-wrap: wrap;
		align-items: center;
		gap: 7px;
		font-size: 11px;
		color: #b1bac6;
		margin: 16px 0;
		overflow-wrap: anywhere;
	}
	.latency {
		font-size: 1.2em;
		white-space: nowrap;
		flex-shrink: 0;
		font-variant-numeric: tabular-nums;
	}
	.status-dot {
		flex: 0 0 6px;
		height: 6px;
		border-radius: 50%;
		background: #b2a385;
	}
	.connected .status-dot {
		background: #86daad;
		box-shadow: 0 0 8px #86daad44;
	}
	.controllers {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(min(100%, 280px), 1fr));
		gap: clamp(10px, 1.8vw, 22px);
	}
	.controller-card {
		min-width: 0;
		background: #19222d;
		border: 1px solid #303c49;
		border-radius: 12px;
		padding: clamp(10px, 1.5vw, 20px);
	}
	.card-heading {
		display: flex;
		align-items: center;
		justify-content: space-between;
		flex-wrap: wrap;
		gap: 6px;
		margin-bottom: 8px;
	}
	h2 {
		display: flex;
		align-items: center;
		gap: 7px;
		font-size: 12px;
		margin: 0;
		font-weight: 600;
	}
	.port {
		display: grid;
		place-items: center;
		width: 22px;
		height: 22px;
		background: #303e4c;
		border-radius: 5px;
		color: #dce5ee;
		font-size: 11px;
	}
	footer {
		border-top: 1px solid #303c49;
		margin-top: 8px;
		padding-top: 10px;
		display: flex;
		align-items: center;
		justify-content: space-between;
		gap: 5px;
		color: #9eadbe;
		font-size: 9px;
		letter-spacing: 0.05em;
	}
	footer div {
		display: flex;
		gap: 10px;
		font-size: 11px;
	}
	b {
		display: inline-block;
		min-width: 3ch;
		text-align: right;
		color: #e0e7f0;
		font-variant-numeric: tabular-nums;
		font-weight: 500;
	}
	.empty {
		color: #afbdca;
		font-size: 13px;
		padding: 24px 0;
	}
	@media (max-width: 360px) {
		.controller-card :global(svg) {
			max-height: 168px;
		}
		.dashboard {
			padding: 8px;
		}
		.controllers {
			gap: 8px;
		}
		.controller-card {
			padding: 8px;
		}
		.card-heading {
			margin-bottom: 4px;
		}
		footer {
			margin-top: 6px;
			padding-top: 8px;
		}
	}
	.minimal-option {
		display: block;
		margin-top: 16px;
	}
	.indicator-option {
		display: flex;
		align-items: center;
		gap: 7px;
		margin-top: 12px;
		cursor: pointer;
	}
	.indicator-option input {
		flex-shrink: 0;
	}
	.minimal header,
	.minimal .card-heading,
	.minimal footer,
	.minimal .empty {
		display: none;
	}
	.minimal .controller-card {
		background: transparent;
		border: 0;
		border-radius: 0;
		padding: 0;
	}
	.minimal {
		padding: 8px;
	}
	.minimal .connection {
		position: fixed;
		top: 12px;
		left: 12px;
		z-index: 3;
		margin: 0;
		gap: 7px;
		flex-wrap: nowrap;
	}
	.exit-minimal {
		position: fixed;
		top: 6px;
		right: 6px;
		z-index: 3;
		display: grid;
		place-items: center;
		width: 32px;
		height: 32px;
		padding: 0;
		background: transparent;
		border: 0;
		color: #9ca6b0;
		opacity: 0.4;
	}
	.exit-minimal:hover,
	.exit-minimal:focus-visible {
		opacity: 1;
		background: #202a35;
	}
</style>
