<script lang="ts">
	import { tick } from 'svelte';
	let {
		name,
		number,
		y,
		width = 240,
		subdued = false,
		onrename
	}: {
		name: string;
		number: number;
		y: number;
		width?: number;
		subdued?: boolean;
		onrename?: (name: string) => void;
	} = $props();
	let editing = $state(false);
	let draft = $state('');
	let input = $state<HTMLInputElement>();
	let button = $state<HTMLButtonElement>();
	async function edit() {
		draft = name;
		editing = true;
		await tick();
		input?.focus();
		input?.select();
	}
	async function finish(save: boolean, restoreFocus = false) {
		if (!editing) return;
		editing = false;
		if (save) onrename?.(draft.trim() || `Pad ${number}`);
		if (restoreFocus) {
			await tick();
			button?.focus();
		}
	}
</script>

<foreignObject x={(440 - width) / 2} {y} {width} height="28">
	{#if editing}
		<input
			bind:this={input}
			bind:value={draft}
			aria-label={`Name for controller ${number}`}
			maxlength="24"
			onblur={() => finish(true)}
			onkeydown={(event) => {
				if (event.key === 'Enter' || event.key === 'Escape') {
					event.preventDefault();
					event.stopPropagation();
					void finish(event.key === 'Enter', true);
				}
			}}
		/>
	{:else}
		<button
			bind:this={button}
			class:subdued
			onclick={edit}
			title={`${name} — click to rename`}
			aria-label={`Rename controller ${number}: ${name}`}>{name}</button
		>
	{/if}
</foreignObject>

<style>
	button,
	input {
		box-sizing: border-box;
		display: block;
		width: 100%;
		height: 28px;
		margin: 0;
		padding: 2px 4px;
		border: 1px solid transparent;
		border-radius: 5px;
		font-family: inherit;
		font-size: 18px;
		font-weight: 700;
		line-height: 22px;
		text-align: center;
		color: #b1bac6;
		background: transparent;
	}
	button {
		cursor: text;
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
		text-shadow: 0 1px 2px #000;
	}
	button.subdued {
		color: #555;
		background: #b3b3b3;
		border: 1.5px solid #939393;
		border-radius: 14px;
		text-shadow: none;
	}
	button:hover,
	button:focus-visible,
	input {
		border-color: #8dd9af;
		background: #202a35;
		color: #b1bac6;
		outline: none;
	}
</style>
