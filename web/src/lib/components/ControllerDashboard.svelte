<script lang="ts">
	import { onMount, untrack, tick } from 'svelte';
	import { emptyState, type ControllerState } from '../controller';
	import {
		ALL_CONTROLLERS,
		parseVisibility,
		SETTINGS_KEY,
		MINIMAL_KEY,
		BACKGROUND_KEY,
		DEFAULT_BACKGROUND
	} from '../settings';
	import N64Controller from './N64Controller.svelte';
	let {
		controllers = Array.from({ length: 4 }, emptyState),
		connection = 'connecting…',
		connected = false,
		initialVisible = ALL_CONTROLLERS,
		initialMinimal = false,
		initialBackground = DEFAULT_BACKGROUND,
		persistSettings = true
	}: {
		controllers?: ControllerState[];
		connection?: string;
		connected?: boolean;
		initialVisible?: number[];
		initialMinimal?: boolean;
		initialBackground?: string;
		persistSettings?: boolean;
	} = $props();
	let visible = $state<number[]>(untrack(() => [...initialVisible]));
	let storageMessage = $state('');
	const inputId = $props.id();
	let background = $state(untrack(() => initialBackground));
	let backgroundInput = $state(untrack(() => initialBackground));
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
		backgroundError = !validColor(value);
		if (!backgroundError) {
			background = value.trim();
			save(BACKGROUND_KEY, background);
		}
	}
	let minimal = $state(untrack(() => initialMinimal));
	let exitButton = $state<HTMLButtonElement>();
	let settingsSummary = $state<HTMLElement>();
	// Initialize from props without tying a user's selection to incoming frames.
	onMount(() => {
		visible = [...initialVisible];
		if (persistSettings) {
			try {
				visible = parseVisibility(localStorage.getItem(SETTINGS_KEY));
				minimal = localStorage.getItem(MINIMAL_KEY) === 'true';
				const savedBackground = localStorage.getItem(BACKGROUND_KEY);
				// A malformed color preference must not prevent restoring other settings.
				try {
					const value: unknown = savedBackground === null ? null : JSON.parse(savedBackground);
					if (validColor(value)) background = backgroundInput = value;
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
					<label class="minimal-option"
						><input
							type="checkbox"
							checked={minimal}
							onchange={(event) => setMinimal(event.currentTarget.checked)}
						/> Minimal interface</label
					>
					<p>Controllers only. Use the corner button or Esc to exit.</p>
					<label class="background-label" for={`${inputId}-background`}
						>Background color (CSS)</label
					>
					<div class="background-input">
						<input
							id={`${inputId}-background`}
							type="text"
							value={backgroundInput}
							oninput={(event) => setBackground(event.currentTarget.value)}
							spellcheck="false"
							autocomplete="off"
							aria-invalid={backgroundError}
							aria-describedby={`${inputId}-background-help`}
						/>
						<button onclick={() => setBackground(DEFAULT_BACKGROUND)}>Reset</button>
					</div>
					<p id={`${inputId}-background-help`} class:color-error={backgroundError} role="status">
						{backgroundError
							? 'Enter a valid CSS color. The last valid color is still applied.'
							: 'Use a CSS color, e.g. #00ff00, rgb(0 255 0), or transparent.'}
					</p>
					<p>{persistSettings ? 'Saved in this browser.' : 'Demo settings — not saved.'}</p>
					{#if storageMessage}<p role="status">{storageMessage}</p>{/if}
				</div>
			</details>
		</header>
		<div class="connection" class:connected><span class="status-dot"></span>{connection}</div>
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
		align-items: center;
		gap: 7px;
		font-size: 11px;
		color: #b1bac6;
		margin: 16px 0;
		overflow-wrap: anywhere;
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
		display: flex;
		align-items: center;
		gap: 7px;
		margin-top: 16px;
		cursor: pointer;
	}
	.minimal header,
	.minimal .connection,
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
