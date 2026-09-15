# N64 Spy web UI

The SvelteKit user interface (UI) reads the ESP32's binary WebSocket messages at `/ws`.
It shows the latest controller frame and combines updates for each animation frame.
It reconnects after one second.
Five-byte frames include a controller index. The UI also supports legacy four-byte frames.

## Development

Use Node.js 22.12+ and npm.

1. Install the dependencies:

   ```sh
   npm ci
   ```

2. Start the development server:

   ```sh
   npm run dev
   ```

3. Check the code:

   ```sh
   npm run check
   ```

4. Run the unit tests:

   ```sh
   npm test
   ```

5. Build the UI:

   ```sh
   npm run build
   ```

`npm run build` prerenders the page with `@sveltejs/adapter-static` and SvelteKit's `output.bundleStrategy: 'inline'`.
The build embeds JavaScript and CSS in `build/index.html`.
The ESP32 needs no Node server or filesystem upload.

For development with hardware, proxy `/ws` to the ESP32 with `ESP32_PROXY=http://n64spy.local npm run dev`.
An IP address also works.

From the repository root, `pio run` installs locked npm dependencies when needed and builds the UI.
Then it embeds the HTML in a generated PROGMEM header under the PlatformIO environment's build directory.
The firmware compiles after this step.
A build failure stops firmware compilation, which prevents the build from embedding an old UI.

Edit files under `web/src/`.
Do not commit generated build files.

## Four-controller display and OBS

The dashboard keeps a separate state for each of the four ports.
Settings lets you show any subset, such as only controller 3 or controllers 1 and 4.
The browser saves selections in localStorage for this browser and origin.
Hidden controllers still receive updates.
The UI assigns legacy four-byte frames to controller 1.

The inline SVG controllers are grayscale at rest.
When pushed, the A, B, C, and Start buttons turn blue, green, yellow, and red, respectively.
The D-pad and shoulder buttons turn gray.
The analog stick follows both axes.
A separate callout beside the center grip shows the rear Z trigger.

Cards stack automatically in a narrow window.
For Open Broadcaster Software (OBS), add the ESP URL as a Browser Source.
Try 280 × 1080 for a sidebar with four controllers.
Configure the selection with OBS's Interact command.
OBS stores settings separately from your regular browser.

The connection indicator shows the browser's WebSocket connection to the ESP32.
It does not show individual controller activity.
The browser checks the connection each second. It sends `ping` only after at least one second without a valid controller frame or `pong`.
The firmware replies with `pong`, so idle controllers do not cause a connection timeout.
After three seconds without a valid controller frame or `pong`, the browser marks the connection lost at the next check.
Detection normally takes three to four seconds. Background tabs can take longer if the browser delays timers.
Connection attempts also time out after three seconds. The browser retries after one second.
Flash the updated firmware and reload the page to use the heartbeat.
After a connection loss, controllers keep the last input state they received.

## Storybook

```sh
npm run storybook        # http://localhost:6006
npm run build-storybook # standalone demos in storybook-static/
```

Storybook includes these examples:

- Four-controller, selected-port, empty, waiting, and disconnected states
- Individual button and stick examples
- A 280 × 1080 OBS viewport
- An animated demo with four controllers

The visibility story runs an interaction test for controller selection.
Storybook settings are separate from the application's saved settings.
The accessibility addon lets you inspect each example.
Storybook is for development only. The firmware HTML bundle does not include it.

## Minimal interface

Enable **Minimal interface** in Settings for a view that shows only controllers.
This view hides the page header, connection status, card headings, borders, and analog readout footers.
The browser saves this preference separately from controller visibility.

A small button in the top-right corner restores the full interface.
**Escape** does the same.
The button supports keyboard access and stays available even when you select no controllers.
Storybook includes minimal, narrow OBS, empty, and toggle demos.

## Background color

Settings includes a **Background color (CSS)** input with a live preview.
The browser saves the color.
Enter a hex value, named color, `rgb(...)`, `hsl(...)`, or `transparent`.
Invalid input leaves the last valid background in place.
Reset restores the default dark background.

The color covers the full viewport.
Use minimal mode to remove card backgrounds for a uniform OBS chroma-key background.
