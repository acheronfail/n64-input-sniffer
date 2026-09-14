// Host test: g++ -std=c++11 -Wall -Wextra -Werror -Iinclude
// test/controller_commands_test.cpp -o /tmp/n64-commands-test && /tmp/n64-commands-test
#include "controller_commands.h"
#include <assert.h>
#include <stdio.h>

using Commands = ControllerCommands;
using Action = Commands::Action;
using Led = Commands::Led;

static void checkCommand(uint16_t button, Action expected, uint32_t start) {
  Commands commands;
  commands.input(0, Commands::Chord, start);
  assert(commands.led(start) == Led::Green);
  commands.input(0, Commands::Chord | button, start + 1);
  for (uint32_t phase = 0; phase < 8; ++phase) {
    const uint32_t now = start + 1 + phase * 125;
    assert(commands.tick(now) == Action::None);
    assert(commands.led(now) == (phase % 2 ? Led::Off : Led::Magenta));
    // More button presses during confirmation must not replace or restart the command.
    commands.input(0, Commands::Chord | Commands::Start | Commands::Z, now);
    assert(commands.tick(now + 124) == Action::None);
    assert(commands.led(now + 124) == (phase % 2 ? Led::Off : Led::Magenta));
  }
  assert(commands.tick(start + 1001) == expected);
  assert(commands.led(start + 1001) == Led::Normal);
  assert(commands.tick(start + 1002) == Action::None);
  commands.input(0, Commands::Chord, start + 1003);
  assert(commands.led(start + 1003) == Led::Normal); // Held chord cannot rearm.
  commands.input(0, 0, start + 1004);
  commands.input(0, Commands::Chord, start + 1005);
  assert(commands.led(start + 1005) == Led::Green);
}

int main() {
  checkCommand(Commands::Start, Action::ResetWiFi, 0);
  checkCommand(Commands::Z, Action::TogglePowerLed, 100);
  checkCommand(Commands::Z, Action::TogglePowerLed, UINT32_MAX - 500);

  Commands commands;
  commands.input(0, 0x0030, 0); // L + R alone is insufficient.
  assert(commands.led(0) == Led::Normal);
  commands.input(0, Commands::Chord | Commands::Start, 1);
  commands.input(0, Commands::Chord | Commands::Start, 2);
  assert(commands.led(2) == Led::Green); // START was held at entry.
  commands.input(1, Commands::Z, 3);
  assert(commands.led(3) == Led::Green); // The other controller cannot send a command.
  commands.input(0, 0x4000, 4); // B no longer triggers WiFi reset.
  assert(commands.led(4) == Led::Green);
  commands.input(0, Commands::Start | Commands::Z, 5);
  assert(commands.led(5) == Led::Green);
  commands.input(0, 0, 6);
  commands.input(0, Commands::Start, 5001); // Exact deadline is too late.
  assert(commands.led(5001) == Led::Normal);
  assert(commands.tick(9000) == Action::None);

  Commands timeout;
  timeout.input(3, Commands::Chord, UINT32_MAX - 2000);
  assert(timeout.tick(2998) == Action::None);
  assert(timeout.led(2998) == Led::Green);
  assert(timeout.tick(2999) == Action::None);
  assert(timeout.led(2999) == Led::Normal); // Timeout without incoming frames.

  Commands lastMoment;
  lastMoment.input(2, Commands::Chord, 0);
  lastMoment.input(2, 0, 1);
  lastMoment.input(2, Commands::Z, 4999);
  assert(lastMoment.led(4999) == Led::Magenta);
  assert(lastMoment.tick(5999) == Action::TogglePowerLed);
  puts("Controller command tests passed.");
}
