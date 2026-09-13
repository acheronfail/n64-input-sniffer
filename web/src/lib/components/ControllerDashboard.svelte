<script lang="ts">
	import { onMount, untrack } from 'svelte';
	import { emptyState, type ControllerState } from '../controller';
	import { ALL_CONTROLLERS, parseVisibility, SETTINGS_KEY } from '../settings';
	import N64Controller from './N64Controller.svelte';
	let {
		controllers = Array.from({ length: 4 }, emptyState),
		received = [false, false, false, false],
		connection = 'connecting…',
		connected = false,
		initialVisible = ALL_CONTROLLERS,
		persistSettings = true
	}: {
		controllers?: ControllerState[];
		received?: boolean[];
		connection?: string;
		connected?: boolean;
		initialVisible?: number[];
		persistSettings?: boolean;
	} = $props();
	let visible = $state<number[]>(untrack(() => [...initialVisible]));
	let storageMessage = $state('');
	// Initialize from props without tying a user's selection to incoming frames.
	onMount(() => {
		visible = [...initialVisible];
		if (persistSettings) {
			try {
				visible = parseVisibility(localStorage.getItem(SETTINGS_KEY));
			} catch {
				storageMessage = 'Browser storage unavailable. Settings apply for this visit.';
			}
		}
	});
	function select(indices: number[]) {
		visible = indices;
		if (persistSettings) {
			try {
				localStorage.setItem(SETTINGS_KEY, JSON.stringify(visible));
				storageMessage = '';
			} catch {
				storageMessage = 'Could not save settings. Settings apply for this visit.';
			}
		}
	}
</script>

<main class="dashboard">
	<header>
		<div class="brand">
			<span class="brand-mark" aria-hidden="true">N</span>
			<div>
				<h1>N64 SPY</h1>
				<p>CONTROLLER INPUTS</p>
			</div>
		</div>
		<details class="settings">
			<summary>Settings</summary>
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
					<h2><span class="port">{index + 1}</span>Controller {index + 1}</h2>
					<span class="signal"
						>{!received[index] ? 'No input yet' : connected ? 'Receiving' : 'Last input'}</span
					>
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

<style>
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
	.signal {
		color: #a1aebe;
		font-size: 10px;
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
</style>
