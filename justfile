# Prerequisites: just, PlatformIO (pio), and Node.js 22.12+ with npm.

_default:
    just -l

# Install web development dependencies and PlatformIO platforms, tools, and libraries.
setup:
    npm --prefix web ci
    pio pkg install

# Build the firmware and embedded web UI for the default PlatformIO environment.
build:
    pio run

# Build and flash the default USB target; PlatformIO auto-detects the upload port.
flash:
    pio run --target upload

# Start the Storybook development server.
storybook:
    npm --prefix web run storybook
