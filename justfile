# Prerequisites: just, PlatformIO (pio), and Node.js 22.12+ with npm.

set positional-arguments

_default:
    just -l

# Install web development dependencies and PlatformIO platforms, tools, and libraries.
setup:
    npm --prefix web ci
    pio pkg install

# Build the firmware and embedded web UI for the default PlatformIO environment.
build:
    pio run

# Build and flash the firmware. Pass extra arguments to PlatformIO.
flash *args:
    pio run --target upload "$@"

# Start the web development server against an ESP32 hostname or IP address.
dev backend="n64spy.lan":
    ESP32_PROXY="http://$1" npm --prefix web run dev

# Start the Storybook development server.
storybook:
    npm --prefix web run storybook
