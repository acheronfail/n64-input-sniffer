# N64 Spy web UI

The SvelteKit UI consumes the ESP32's existing binary WebSocket API at `/ws`.
It displays the latest controller frame, coalesces updates per animation frame,
and reconnects after one second. Five-byte frames include a controller index;
legacy four-byte frames are also supported.

Use Node.js 22.12+ and npm:

```sh
npm ci
npm run dev
npm run check
npm test
npm run build
```

`npm run build` prerenders the page with `@sveltejs/adapter-static` and
SvelteKit's `output.bundleStrategy: 'inline'`, embedding JavaScript and CSS in
`build/index.html`. No Node server or filesystem upload is needed on the ESP32.

For live development against hardware, proxy `/ws` to the ESP32 by setting
`ESP32_PROXY=http://n64spy.local npm run dev` (an IP address also works).

From the repository root, `pio run` installs locked npm dependencies when needed,
builds the UI, then embeds the HTML in a generated PROGMEM header under the
PlatformIO environment's build directory before compiling the firmware.
Build failures stop firmware compilation so stale UI cannot be embedded.
Edit files under `web/src/`; generated build files should not be committed.
