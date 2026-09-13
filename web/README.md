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

## Four-controller display and OBS

The dashboard keeps independent state for all four ports. Settings lets you show
any subset (including only controller 3 or controllers 1 and 4); selections are
saved in localStorage for this browser and origin. Hidden controllers continue
receiving updates. Legacy four-byte frames are assigned to controller 1.

The inline SVG controllers are greyscale at rest. Pressed A, B, C and Start
buttons light up blue, green, yellow and red respectively; the D-pad and shoulder
buttons highlight in grey. The analog stick follows both axes. The rear Z trigger
is shown in a separate callout beside the center grip.

Cards automatically stack in a narrow window. For OBS, add the ESP URL as a
Browser Source and try 280 × 1080 for a four-controller sidebar. Configure its
selection using OBS's Interact command. OBS stores settings separately from your
regular browser. The connection indicator describes the browser’s WebSocket
connection to the ESP32, not individual controller activity. Controllers retain
the last received input state after a connection loss.

## Storybook

```sh
npm run storybook        # http://localhost:6006
npm run build-storybook # standalone demos in storybook-static/
```

Storybook includes four-controller, selected-port, empty, waiting and disconnected
states, individual button/stick examples, a 280 × 1080 OBS viewport, and an animated
four-controller demo. The visibility story runs an interaction test for controller
selection. Storybook settings are isolated from the application's saved settings.
The accessibility addon is available for inspecting each example.

Storybook is development-only and is not included in the firmware HTML bundle.

Enable **Minimal interface** in Settings for a controllers-only view, without the
page header, connection status, card headings, borders, or analog readout footers.
This preference is saved separately from controller visibility. A subtle button
in the top-right corner restores the full interface; **Escape** does the same.
The button is keyboard accessible and remains available even if no controllers
are selected. Storybook includes minimal, narrow OBS, empty, and toggle demos.

Settings includes a **Background color (CSS)** input with live preview and browser
persistence. Enter a hex value, named color, `rgb(...)`, `hsl(...)`, or `transparent`.
Invalid input leaves the last valid background in place; Reset restores the default
dark background. The color covers the entire viewport. Use minimal mode to remove
card backgrounds for a uniform OBS chroma-key background.
