<script lang="ts">
	import './layout.css';
	import favicon from '$lib/assets/favicon.svg?inline';
	let { children } = $props();
</script>

<svelte:head>
	<link rel="icon" type="image/svg+xml" href={favicon} />
</svelte:head>

{@render children()}
