<script lang="ts">
	let { direction }: { direction: string } = $props();
	const rotations: Record<string, number> = {
		UP: 0,
		CUP: 0,
		RIGHT: 90,
		CRIGHT: 90,
		DOWN: 180,
		CDOWN: 180,
		LEFT: 270,
		CLEFT: 270
	};
</script>

<!-- Center the triangle's area at the origin, independent of font metrics. -->
<path d="M0 -7L6 3.5H-6Z" transform={`rotate(${rotations[direction] ?? 0})`} />
