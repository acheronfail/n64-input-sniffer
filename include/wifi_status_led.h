#pragma once

#include <stdint.h>
#include "controller_commands.h"

// Timing only. The LED task owns this state. WS2812 colors use green, red, blue (GRB) order.
class WiFiStatusLed {
public:
  static constexpr uint32_t Red = 0x00FF00;
  static constexpr uint32_t Green = 0xFF0000;
  static constexpr uint32_t Blue = 0x0000FF;
  static constexpr uint32_t SuccessMs = 1000; // Two 250 ms on/off flashes.
  static constexpr uint32_t FailureMs = 750;  // Three 125 ms on/off flashes.

  uint32_t color(uint32_t now, bool connected, bool portal,
                 uint32_t failures, bool powerEnabled,
                 ControllerCommands::Led command) {
    const Mode next = connected ? Mode::Normal : portal ? Mode::Portal : Mode::Connecting;
    if (!initialized || next != base) {
      initialized = true;
      base = next;
      baseStartedAt = now;
    }
    if (connected && !wasConnected) {
      signal = Signal::Success;
      signalStartedAt = now;
    } else if (!connected && failures != seenFailures && signal != Signal::Failure) {
      signal = Signal::Failure;
      signalStartedAt = now;
    } else if (!connected && wasConnected) {
      signal = Signal::Failure;
      signalStartedAt = now;
    }
    wasConnected = connected;
    seenFailures = failures;

    const uint32_t elapsed = now - signalStartedAt;
    if ((signal == Signal::Success && elapsed >= SuccessMs) ||
        (signal == Signal::Failure && elapsed >= FailureMs)) {
      signal = Signal::None;
      baseStartedAt = now;
    }

    // Command feedback, including its off phases, takes priority over WiFi status and the power LED.
    switch (command) {
    case ControllerCommands::Led::Green: return Green;
    case ControllerCommands::Led::Magenta: return 0x00FFFF;
    case ControllerCommands::Led::Off: return 0;
    case ControllerCommands::Led::Normal: break;
    }
    if (signal == Signal::Success) return (elapsed / 250) % 2 ? 0 : Green;
    if (signal == Signal::Failure) return (elapsed / 125) % 2 ? 0 : Red;
    if (base == Mode::Normal) return powerEnabled ? Red : 0;
    return ((uint32_t(now - baseStartedAt) / 500) % 2) ? 0 :
           base == Mode::Portal ? Red : Blue;
  }

private:
  enum class Mode { Connecting, Portal, Normal };
  enum class Signal { None, Success, Failure };
  Mode base = Mode::Connecting;
  Signal signal = Signal::None;
  bool initialized = false;
  bool wasConnected = false;
  uint32_t seenFailures = 0;
  uint32_t baseStartedAt = 0;
  uint32_t signalStartedAt = 0;
};
