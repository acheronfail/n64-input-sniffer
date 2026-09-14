#pragma once

#include <stddef.h>
#include <stdint.h>

// Button masks use the first two packed N64 response bytes, most significant bit (MSB) first.
class ControllerCommands {
public:
  enum class Action { None, ResetWiFi, TogglePowerLed };
  enum class Led { Normal, Green, Magenta, Off };
  static constexpr uint16_t Start = 0x1000;
  static constexpr uint16_t Z = 0x2000;
  static constexpr uint16_t Chord = 0x0430; // D-pad down + L + R
  static constexpr uint32_t ListenMs = 5000;
  static constexpr uint32_t ConfirmationFlashMs = 125;
  static constexpr uint32_t ConfirmationFlashCount = 4;

  void input(size_t controller, uint16_t buttons, uint32_t now) {
    if (controller >= 4) return;
    const uint16_t previous = previousButtons[controller];
    previousButtons[controller] = buttons;
    expire(now);
    if (mode == Mode::Confirming) return;

    if (mode == Mode::Idle) {
      if ((buttons & Chord) == Chord && (previous & Chord) != Chord) {
        owner = controller;
        startedAt = now;
        mode = Mode::Listening;
      }
      return; // Buttons already held with the chord are not commands.
    }
    if (controller != owner) return;
    const uint16_t pressed = buttons & ~previous;
    // Ignore ambiguous simultaneous commands. Release the buttons. Then push one command button.
    const uint16_t command = pressed & (Start | Z);
    if (command == Start || command == Z) {
      pending = command == Start ? Action::ResetWiFi : Action::TogglePowerLed;
      startedAt = now;
      mode = Mode::Confirming;
    }
  }

  // Return the action once, after four complete 125 ms on/off flashes (one second).
  Action tick(uint32_t now) {
    expire(now);
    if (mode == Mode::Confirming &&
        uint32_t(now - startedAt) >= 2 * ConfirmationFlashCount * ConfirmationFlashMs) {
      mode = Mode::Idle;
      const Action result = pending;
      pending = Action::None;
      return result;
    }
    return Action::None;
  }

  Led led(uint32_t now) const {
    if (mode == Mode::Listening) return Led::Green;
    if (mode == Mode::Confirming) {
      return ((uint32_t(now - startedAt) / ConfirmationFlashMs) % 2 == 0)
                 ? Led::Magenta : Led::Off;
    }
    return Led::Normal;
  }

private:
  enum class Mode { Idle, Listening, Confirming };
  Mode mode = Mode::Idle;
  Action pending = Action::None;
  uint16_t previousButtons[4] = {};
  size_t owner = 0;
  uint32_t startedAt = 0;

  void expire(uint32_t now) {
    if (mode == Mode::Listening && uint32_t(now - startedAt) >= ListenMs) {
      mode = Mode::Idle;
    }
  }
};
