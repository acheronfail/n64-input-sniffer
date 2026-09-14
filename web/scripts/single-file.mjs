import { readFile, readdir, rm } from 'node:fs/promises';

const build = new URL('../build/', import.meta.url);
const html = await readFile(new URL('index.html', build), 'utf8');
const markup = html.replace(/(<script\b[^>]*>)[\s\S]*?<\/script>/gi, '$1</script>');
// Fail if the HTML file needs extra assets.
if (
	/<script\b[^>]*\bsrc\s*=/i.test(markup) ||
	/<link\b[^>]*\brel\s*=\s*["'](?:stylesheet|modulepreload|preload)["']/i.test(markup) ||
	/(?:src|href)\s*=\s*["'](?!data:|#)[^"']+["']/i.test(markup) ||
	/\burl\(\s*["']?(?!data:|#)/i.test(markup)
) {
	throw new Error('The firmware UI must inline all scripts, styles and assets');
}
// SvelteKit also writes unused server CSS and version metadata.
// Version polling is disabled. The ESP serves only index.html, so discard these extra files.
await rm(new URL('_app/', build), { recursive: true, force: true });
const files = await readdir(build);
if (files.length !== 1 || files[0] !== 'index.html') {
	throw new Error(`Expected only build/index.html; got ${files.join(', ')}`);
}
console.log(`Single-file firmware UI: ${Buffer.byteLength(html)} bytes`);
