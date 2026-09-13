import { loadEnv } from 'vite';
import tailwindcss from '@tailwindcss/vite';
import { defineConfig } from 'vitest/config';
import adapter from '@sveltejs/adapter-static';
import { sveltekit } from '@sveltejs/kit/vite';

const { ESP32_PROXY } = loadEnv('development', '.', 'ESP32_');

export default defineConfig({
	server: {
		proxy: ESP32_PROXY ? { '/ws': { target: ESP32_PROXY, ws: true } } : undefined
	},
	plugins: [
		{
			name: 'inline-bundle-import-meta',
			apply: 'build',
			configEnvironment(name, config) {
				const output = (config.build?.rolldownOptions ?? config.build?.rollupOptions)?.output;
				if (name !== 'client' || !output || Array.isArray(output) || output.format !== 'iife') {
					return;
				}
				return {
					build: {
						rolldownOptions: {
							transform: {
								// Inline scripts resolve URLs against their document and have no module hooks.
								define: {
									'import.meta.url': 'document.baseURI',
									'import.meta.resolve': 'undefined',
									'import.meta.hot': 'undefined'
								}
							}
						}
					}
				};
			}
		},
		tailwindcss(),
		sveltekit({
			compilerOptions: {
				// Force runes mode for the project, except for libraries. Can be removed in svelte 6.
				runes: ({ filename }) =>
					filename.split(/[/\\]/).includes('node_modules') ? undefined : true
			},
			adapter: adapter(),
			output: { bundleStrategy: 'inline' },
			version: { name: 'embedded', pollInterval: 0 }
		})
	],
	test: {
		expect: { requireAssertions: true },
		projects: [
			{
				extends: './vite.config.ts',
				test: {
					name: 'server',
					environment: 'node',
					include: ['src/**/*.{test,spec}.{js,ts}'],
					exclude: ['src/**/*.svelte.{test,spec}.{js,ts}']
				}
			}
		]
	}
});
