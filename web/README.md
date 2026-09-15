# N64 Spy web UI

The SvelteKit user interface (UI) reads the ESP32's binary WebSocket messages at `/ws`.
It shows the latest controller frame and combines updates for each animation frame.
It reconnects after one second.
Thirteen-byte frames include a controller index and a decode timestamp. The UI also supports legacy four-byte and five-byte frames.

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
The browser checks the connection each second. It sends `ping` only after at least one second without a valid controller frame, clock reply, or `pong`.
The firmware replies with `pong`, so idle controllers do not cause a connection timeout.
After three seconds without a valid controller frame, clock reply, or `pong`, the browser marks the connection lost at the next check.
Detection normally takes three to four seconds. Background tabs can take longer if the browser delays timers.
Connection attempts also time out after three seconds. The browser retries after one second.
Flash the updated firmware and reload the page to use the heartbeat.
After a connection loss, controllers keep the last input state they received.

## Input latency

The connection row shows `Link latency: ≈5 ms` after the first clock reply, even without controller input.
Clock replies serve as timestamped heartbeats. The browser sends one clock probe per second, including during input activity.
Link latency estimates the time from ESP reply to browser receipt. It excludes the input queue delay.
For three seconds after a measured input change, the row shows `Input latency` instead.
The browser smooths input and link readings separately. If clock replies stop, the link reading becomes stale after three seconds.
Input latency estimates the time from ESP decode to browser receipt, including the firmware queue and network delay.
It excludes console polling, capture delay before decoding, and screen display delay.
The browser smooths readings and updates the label once per second.
A dash means that no measurement is available. Minimal mode hides the label by default.
Use **Show latency in minimal mode** in Settings to show or hide the latency.
The browser saves this setting. It is off by default.
The latency follows the connection dot in a row at the top left.
If you hide the dot, the latency stays at the top left.

It uses the shortest round trip from the last 30 seconds to estimate the clock offset.
Clock checks expire after 30 seconds. Reconnection clears the estimate and the last reading.
Unequal network delays affect accuracy, so the value retains the approximation symbol.

Controller packets contain 13 bytes:

- Byte 0: controller index, from 0 to 3.
- Bytes 1–4: button and stick state, in the existing format.
- Bytes 5–12: unsigned 64-bit ESP decode timestamp in microseconds, least significant byte first.

A zero timestamp marks a state without a measured decode time.
Retries preserve the timestamp. The browser excludes cached states from before its first clock check.
The browser still accepts legacy four-byte and five-byte packets, which have no latency measurement.
Reload the page after flashing the firmware. Older pages cannot decode the new packets.

Clock requests use `sync:<id>`. Replies use `sync:<id>:<receivedUs>:<repliedUs>`.
The ESP records both times with its monotonic timer. The browser records send and receive times with `performance.now()`.
All calculations use milliseconds. The clock offset equals ESP time minus browser time:

```text
offset = ((espReceived - browserSent) + (espReplied - browserReceived)) / 2
roundTrip = (browserReceived - browserSent) - (espReplied - espReceived)
latency = browserReceived - espDecoded + offset
```

Valid clock replies also count as connection activity. The existing idle ping/pong check remains active.

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

Select **Enter minimal interface** in Settings for a view that shows only controllers.
This view hides the page header, connection text, card headings, borders, and analog readout footers.
A small dot at the top left shows the connection state: green when connected, tan when connecting or disconnected.
Use **Show connection dot in minimal mode** in Settings to show or hide the dot.
The checkbox defaults to checked, and the browser saves your choice.
The browser saves this preference separately from controller visibility.

A small button in the top-right corner restores the full interface.
**Escape** does the same.
The button supports keyboard access and stays available even when you select no controllers.
Storybook includes minimal, narrow OBS, empty, and toggle demos.

## Background

The background defaults to **Transparent**, including when you select **Enter minimal interface**.
Use this option for an OBS overlay.
The page body has a dark background for regular browsers.
The default OBS custom CSS overrides this background with transparency.
Select **Color** to use a chroma key background instead.
These options are mutually exclusive.

The **Background color (CSS)** input is available only when you select **Color**.
Enter a hex value, named color, `rgb(...)`, or `hsl(...)`.
Invalid input leaves the last valid background in place.
**Reset** selects **Transparent**.
The browser saves the selected background and restores existing saved colors.

The background covers the full viewport.
Use minimal mode to remove card backgrounds and show only the controllers.
