# NintendoSpy N64 reader — ESP32

This PlatformIO/Arduino port reads Nintendo 64 (N64) controller input with NintendoSpy's single-wire protocol support.
It supports only the N64 controller protocol.
The ESP32 passively reads up to 4 controller DATA lines and sends the decoded input over serial.
It never drives the line.

The port uses the project's AVR firmware ([../firmware/firmware.ino](../firmware/firmware.ino), `loop_N64`)
and the packet layout in [../Readers/Nintendo64.cs](../Readers/Nintendo64.cs).

## How it works

The N64 controller uses one open-collector wire that stays high when idle. Each bit is a ~4µs pulse:

| Bit | Low  | High |
| --- | ---- | ---- |
| `0` | ~3µs | ~1µs |
| `1` | ~1µs | ~3µs |

The ESP32 samples the line ~2µs after each falling edge.
At that point, a `1` is high and a `0` is still low.
Each polled frame starts with the console's 9-bit prefix: the `0x01` poll command (`0000_0001`) and a `1` stop bit.
The controller's 32-bit response comes next.

The ESP32 port replaces AVR `PIND` reads with direct `GPIO.in` register reads.
It replaces manually counted NOP delays with the Xtensa cycle counter (`xthal_get_ccount`), scaled by `F_CPU`.

## Wiring

> [!WARNING]
> **Do not connect USB-C while the adapter is connected to the N64 console.**
> Fully disconnect the adapter from **all four console ports** before connecting USB-C to a computer or USB power source. Disconnect USB-C before reconnecting the adapter to the console.
>
> **Turning the console off is not enough.** USB power can backfeed the console’s 3.3V rail and potentially damage hardware. The 470 µF capacitor does not prevent backfeeding.

![Four-controller passthrough wiring](docs/n64-esp32-wiring.png)

[Download the wiring graphic (SVG)](docs/n64-esp32-wiring.svg).
The diagram shows the component side of the board, with USB at the top. This matches the supplied Super Mini pinout.
The right-edge pins are **5V, GND, 3V3, GPIO 13, 12, 11, 10, 9, 8**, from top to bottom.
The reference image labels 3V3 as `3V3OUT`.
The diagram simplifies board spacing and shows controller terminals as a schematic.

1. Connect one console port's 3.3V rail to the ESP **3V3** pin. The diagram shows port 1.
2. Connect **GND from that same port** to ESP GND.
3. Keep each controller's power and ground passthrough connections.
4. Connect a **470 µF electrolytic capacitor** across ESP 3V3 and GND, close to the board, with short leads.
   Connect **positive (+) to 3V3**. Connect **negative (striped side) to GND**.
   Use a voltage rating of at least 6.3V.
5. Leave USB disconnected and the ESP 5V pin unconnected while the console supplies power.

One ground tap is enough because all four port grounds connect inside the same N64 console.
The ports need no extra ground bridges.
The 470 µF value comes from the earlier power tests.

The Super Mini's onboard RGB LED defaults to solid red while powered.
The controller command below can disable this power LED. The preference stays saved after a reboot.
The `POWER_LED_PIN=48` flag in `platformio.ini` sets its GPIO for all S3 environments.
The generic `esp32dev` environments leave the LED disabled unless this flag is set.

| N64 connector                | ESP32                                                                     |
| ---------------------------- | ------------------------------------------------------------------------- |
| GND (same port as power tap) | GND                                                                       |
| DATA (middle)                | GPIO 13/12/11/10 (`N64_PIN_1..N64_PIN_4` in [src/main.cpp](src/main.cpp)) |
| 3.3V (tap one console port)  | 3V3, with 470 µF capacitor to GND                                         |

The N64 data line uses 3.3V logic with a pull-up on the console side.
It connects directly to an ESP32 input without level shifting.
**Share a common ground** with the console/controller.

To read a live session, tap the DATA line between the console and controller, for example with a passthrough adapter.
The console must poll the controller for frames to appear.

If your data wires use different GPIOs, change `N64_PIN_1..N64_PIN_4` in [src/main.cpp](src/main.cpp).

## Live web interface (wireless)

The ESP32 serves a small web user interface (UI) that shows the controller state in real time.
You can watch input without a wired serial connection.
The firmware contains no fixed WiFi credentials. You enter them once through a captive portal.

The LED shows WiFi status even when the normal power LED is disabled:

| State                              | LED pattern                                                                             |
| ---------------------------------- | --------------------------------------------------------------------------------------- |
| Connecting or reconnecting         | Blue, 500 ms on / 500 ms off, repeating.                                                |
| Connected (IP address obtained)    | Two green flashes, 250 ms on / 250 ms off, then the normal power LED setting.           |
| Connection failed or lost          | Three red flashes, 125 ms on / 125 ms off, then the connection or setup portal pattern. |
| Setup portal waits for credentials | Red, 500 ms on / 500 ms off, repeating.                                                 |

When you submit credentials, the LED switches to the blue connection pattern.
A successful connection takes priority over the failure flashes.
If the portal times out, the LED shows the failure pattern before the ESP32 reboots.
After the portal saves credentials, the LED shows success before the portal's cleanup reboot.

Controller command feedback takes priority over WiFi status, including during the off phases.
Commands become available after the initial WiFi setup completes.
A background task controls the flashes, including during connection attempts.
The flashes add no delays to controller capture or web updates.

### Connect to WiFi

1. On first boot, join the open **`N64Spy-Setup`** WiFi network from a phone or laptop.
   The ESP32 starts this network automatically. A captive portal page opens automatically.
2. Select your WiFi network on the portal page.
3. Enter the network password.
4. Save the credentials.
   The ESP32 stores them in flash and automatically reconnects to your network on each later boot.
5. Open `http://n64spy.local/` in a browser.
   The serial monitor also prints the assigned IP address and the `http://n64spy.local/` address through multicast DNS (mDNS).
   You can use either address.

The page connects to a WebSocket at `/ws`.
The firmware sends a 5-byte binary frame (`controllerIndex + 4-byte state`) each time the state changes.
The page highlights buttons and moves the stick for the active controller.

To change networks, hold **BOOT** (`WIFI_RESET_PIN`, GPIO 0 on most development boards) for ~3 seconds.
You can do this at startup or during normal operation.
The ESP32 deletes the saved network and reboots into the setup portal.

### Controller commands

1. Push **L + R + D-pad down** together on any controller to enter command mode.
   The LED turns **green** for up to **5 seconds**.
2. During this time, push one command button on the **same controller**.
   You can release the entry combination first.

| Button    | Action                                                                              |
| --------- | ----------------------------------------------------------------------------------- |
| **START** | Delete saved WiFi credentials and reboot into the **N64Spy-Setup** captive network. |
| **Z**     | Switch the normal red power LED on or off and save the preference.                  |

A recognized command ends command mode immediately.
The LED flashes **magenta four times within one second**, each with **125 ms on and 125 ms off**.
Then the ESP32 does the command's action.
Command feedback still lights the LED when the red power LED is disabled.
Capture and web updates continue during the confirmation flashes.

If you held a command button when command mode started, release it. Then push it again.
The ESP32 ignores other buttons and simultaneous START + Z presses until you push one command button or the time expires.
A timeout restores the normal LED setting.
To start another command window, release the entry combination. Then push it again.

The console must run and poll the controller.
Commands are available after startup WiFi setup completes.
The ESP32 is a passive sniffer, so these button presses also reach the game.

### Web server and state format

The asynchronous server runs in its own task on the other core.
It does not disturb the timing of the software that reads individual bits.
The setup portal runs only during startup, before the server starts, so they do not compete for port 80.

The state format uses the following bytes.
See `packState()` in [include/n64_decoder.h](include/n64_decoder.h) and the bit masks in [web/src/lib/controller.ts](web/src/lib/controller.ts).
Bits run from the most significant bit (MSB) to the least significant bit (LSB).

| Byte | Bits (MSB→LSB)                            |
| ---- | ----------------------------------------- |
| 0    | controller index (0..3)                   |
| 1    | A, B, Z, START, UP, DOWN, LEFT, RIGHT     |
| 2    | –, –, L, R, C-UP, C-DOWN, C-LEFT, C-RIGHT |
| 3    | stick X (int8)                            |
| 4    | stick Y (int8)                            |

## Build, upload, monitor

Install Node.js 22.12+ and npm alongside PlatformIO.
Each firmware build first builds the SvelteKit UI in `web/`.
The build installs locked npm dependencies when needed and embeds the UI as a single HTML file in the firmware.
It needs no separate filesystem upload.
See [web/README.md](web/README.md) for UI development and checks.

**Before plugging in USB-C, disconnect the adapter from all four console ports—even if the console is switched off.**

1. Build the firmware:

   ```sh
   pio run
   ```

2. Upload the firmware:

   ```sh
   pio run -t upload
   ```

3. Open the serial monitor at 115200 baud:

   ```sh
   pio device monitor
   ```

## Tests

Run all firmware host tests with `sh scripts/test_host.sh`. These tests need no ESP32.
Run web unit tests with `cd web && npm test`.
See [test/README](test/README) for test coverage and hardware test limitations.

## Output

The firmware logs state changes to keep the serial output readable:

```
[N64 1] A START stick=(0, 0)
[N64 3] UP stick=(-42, 118)
```

The firmware ignores unrecognized frames, such as rumble/mempak commands, that are not controller-state polls.
