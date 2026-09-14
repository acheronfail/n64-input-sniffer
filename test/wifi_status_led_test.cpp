// Host test: c++ -std=c++11 -Wall -Wextra -Werror -Iinclude
// test/wifi_status_led_test.cpp -o /tmp/n64-wifi-led-test && /tmp/n64-wifi-led-test
#include "wifi_status_led.h"
#include <assert.h>
#include <stdio.h>
#include <initializer_list>

using Led = WiFiStatusLed;
using Command = ControllerCommands::Led;

static void checkSignals(uint32_t start) {
  Led led;
  // All status signals remain visible with the power LED disabled.
  for (uint32_t phase = 0; phase < 4; ++phase) {
    const uint32_t now = start + phase * 250;
    assert(led.color(now, true, false, 0, false, Command::Normal) ==
           (phase % 2 ? 0 : Led::Green));
    assert(led.color(now + 249, true, false, 0, false, Command::Normal) ==
           (phase % 2 ? 0 : Led::Green));
  }
  assert(led.color(start + 1000, true, false, 0, false, Command::Normal) == 0);
  assert(led.color(start + 1001, true, false, 0, true, Command::Normal) == Led::Red);
  for (uint32_t phase = 0; phase < 6; ++phase) {
    const uint32_t now = start + 2000 + phase * 125;
    assert(led.color(now, false, false, 1, false, Command::Normal) ==
           (phase % 2 ? 0 : Led::Red));
    assert(led.color(now + 124, false, false, 1, false, Command::Normal) ==
           (phase % 2 ? 0 : Led::Red));
  }
  assert(led.color(start + 2750, false, false, 1, false, Command::Normal) == Led::Blue);
  assert(led.color(start + 3250, false, false, 1, false, Command::Normal) == 0);
  assert(led.color(start + 3500, true, false, 1, false, Command::Normal) == Led::Green);
}

int main() {
  checkSignals(0);
  checkSignals(UINT32_MAX - 500);
  Led boot;
  assert(boot.color(1234, false, false, 0, false, Command::Normal) == Led::Blue);
  assert(boot.color(1733, false, false, 0, false, Command::Normal) == Led::Blue);
  assert(boot.color(1734, false, false, 0, false, Command::Normal) == 0);
  Led led;
  assert(led.color(0, false, false, 0, false, Command::Normal) == Led::Blue);
  assert(led.color(499, false, false, 0, false, Command::Normal) == Led::Blue);
  assert(led.color(500, false, false, 0, false, Command::Normal) == 0);
  assert(led.color(1000, false, false, 0, false, Command::Normal) == Led::Blue);
  assert(led.color(1100, false, true, 0, false, Command::Normal) == Led::Red);
  assert(led.color(1600, false, true, 0, false, Command::Normal) == 0);
  // Credential submission switches portal red to connecting blue.
  assert(led.color(1700, false, false, 0, false, Command::Normal) == Led::Blue);
  assert(led.color(1800, false, false, 1, false, Command::Normal) == Led::Red);
  // A return to the portal or repeated failures must not restart the flashes.
  assert(led.color(1925, false, true, 2, false, Command::Normal) == 0);
  assert(led.color(2549, false, true, 2, false, Command::Normal) == 0);
  assert(led.color(2550, false, true, 2, false, Command::Normal) == Led::Red);
  assert(led.color(3050, false, true, 2, false, Command::Normal) == 0);
  // Controller feedback, including its off phases, takes priority over every network state.
  for (bool connected : {false, true}) {
    assert(led.color(3100, connected, true, 2, true, Command::Green) == Led::Green);
    assert(led.color(3100, connected, true, 2, true, Command::Magenta) == 0x00FFFF);
    assert(led.color(3100, connected, true, 2, true, Command::Off) == 0);
  }
  // A successful reconnect takes priority over an active failure signal.
  assert(led.color(3200, false, false, 3, false, Command::Normal) == Led::Red);
  assert(led.color(3250, true, false, 3, false, Command::Normal) == Led::Green);
  assert(led.color(4250, true, false, 3, false, Command::Normal) == 0);
  puts("Wi-Fi status LED tests passed.");
}
