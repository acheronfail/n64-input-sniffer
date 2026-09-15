#include "n64_decoder.h"
#include <assert.h>
#include <stdio.h>
#include <vector>
#include <algorithm>

// Same fields as an RMT item, without the ESP32 SDK dependency.
struct Pulse { unsigned level0, duration0, level1, duration1; };
using Capture = std::vector<Pulse>;

static Capture pulses(const char *bits, bool reversed = false,
                      unsigned oneLow = 1, unsigned zeroLow = 3,
                      unsigned cell = 4) {
  Capture result;
  for (; *bits; ++bits) {
    const unsigned low = *bits == '1' ? oneLow : zeroLow;
    result.push_back(reversed ? Pulse{1, cell - low, 0, low}
                              : Pulse{0, low, 1, cell - low});
  }
  return result;
}

static void expectPacket(const Capture &capture, const uint8_t expected[4],
                         unsigned ticksPerUs = 1) {
  uint8_t frame[N64_FRAMEBITS] = {};
  assert(decodeFrameFromRmtItems(capture.data(), capture.size(), frame, ticksPerUs));
  assert(hasValidReservedBits(frame));
  uint8_t payload[4];
  packState(frame, payload);
  assert(memcmp(payload, expected, 4) == 0);
}

static void reject(const Capture &capture) {
  uint8_t frame[N64_FRAMEBITS];
  memset(frame, 0xa5, sizeof(frame));
  assert(!decodeFrameFromRmtItems(capture.data(), capture.size(), frame));
  for (auto bit : frame) assert(bit == 0xa5); // Failure leaves output untouched.
}

int main() {
  // Literal wire fixtures: poll byte + stop bit + response, MSB first.
  const char *neutral = "000000011" "00000000" "00000000" "00000000" "00000000";
  const char *mixed = "000000011" "10100101" "00101001" "10000000" "01111111";
  const char *all = "000000011" "11111111" "00111111" "11111111" "00000001";
  const uint8_t neutralPacket[] = {0, 0, 0, 0};
  const uint8_t mixedPacket[] = {0xa5, 0x29, 0x80, 0x7f};
  const uint8_t allPacket[] = {0xff, 0x3f, 0xff, 1};
  // A near-3us zero must stay zero when the capture retains fractional timing.
  for (bool reversed : {false, true}) {
    auto capture = pulses(neutral, reversed, 8, 24, 32);
    capture[9] = reversed ? Pulse{1, 8, 0, 23} : Pulse{0, 23, 1, 8};
    uint8_t frame[N64_FRAMEBITS], payload[4];
    assert(decodeFrameFromRmtItems(capture.data(), capture.size(), frame, 8));
    packState(frame, payload);
    assert(memcmp(payload, neutralPacket, 4) == 0);
    // Integer microseconds lose the distinction and produce a false A press.
    for (auto &p : capture) { p.duration0 /= 8; p.duration1 /= 8; }
    assert(decodeFrameFromRmtItems(capture.data(), capture.size(), frame));
    packState(frame, payload);
    assert(payload[0] == 0x80);
    assert(!decodeFrameFromRmtItems(capture.data(), capture.size(), frame, 0));
  }
  for (bool reversed : {false, true}) {
    expectPacket(pulses(neutral, reversed, 8, 24, 32), neutralPacket, 8);
    expectPacket(pulses(mixed, reversed, 8, 24, 32), mixedPacket, 8);
    expectPacket(pulses(all, reversed, 8, 24, 32), allPacket, 8);
    expectPacket(pulses(neutral, reversed), neutralPacket);
    expectPacket(pulses(mixed, reversed), mixedPacket);
    expectPacket(pulses(all, reversed), allPacket);
    // Threshold: 2us is one, 3us is zero. Longest accepted cell and low pulse.
    expectPacket(pulses(mixed, reversed, 2, 4, 6), mixedPacket);
  }
  // Each button and axis bit independently checks the byte and bit order.
  for (size_t bit = 0; bit < 32; ++bit) {
    if (bit == 8 || bit == 9) continue;
    auto capture = pulses(neutral);
    capture[9 + bit] = Pulse{0, 1, 1, 3};
    uint8_t expected[4] = {};
    expected[bit / 8] = uint8_t(0x80 >> (bit % 8));
    expectPacket(capture, expected);
  }
  for (unsigned low = 0; low <= 5; ++low) {
    for (unsigned high = 0; high <= 7; ++high) {
      assert(isValidN64CellUs(low, high) ==
             (low >= 1 && low <= 4 && low + high >= 3 && low + high <= 6));
    }
  }
  for (size_t count : {size_t(0), size_t(1), size_t(9), size_t(40)}) {
    auto capture = pulses(mixed);
    capture.resize(count);
    reject(capture);
  }
  for (size_t count : {size_t(42), size_t(96), size_t(120)}) {
    auto capture = pulses(mixed);
    capture.resize(count, Pulse{0, 1, 1, 3});
    reject(capture);
  }
  // Wrong command or stop bit, including accessory commands.
  for (unsigned command : {0U, 2U, 3U, 255U}) {
    auto capture = pulses(mixed);
    for (size_t i = 0; i < 8; ++i)
      capture[i] = (command & (0x80 >> i)) ? Pulse{0, 1, 1, 3} : Pulse{0, 3, 1, 1};
    reject(capture);
  }
  auto capture = pulses(mixed);
  capture[8] = Pulse{0, 3, 1, 1};
  reject(capture);
  // Ignore malformed segments. A replacement for a real bit makes the frame too short.
  for (const Pulse noise : {Pulse{0, 0, 1, 4}, Pulse{0, 3, 1, 0},
                           Pulse{0, 1, 1, 1}, Pulse{0, 4, 1, 3},
                           Pulse{0, 5, 1, 1}, Pulse{0, 1, 0, 3},
                           Pulse{1, 1, 1, 3}}) {
    capture = pulses(mixed);
    capture[20] = noise;
    reject(capture);
    capture = pulses(mixed);
    capture.insert(capture.begin() + 20, noise);
    expectPacket(capture, mixedPacket);
  }
  // Check reserved bits separately before state publication or command processing.
  for (size_t bit : {size_t(8), size_t(9)}) {
    capture = pulses(neutral);
    capture[9 + bit] = Pulse{0, 1, 1, 3};
    uint8_t frame[N64_FRAMEBITS];
    assert(decodeFrameFromRmtItems(capture.data(), capture.size(), frame));
    assert(!hasValidReservedBits(frame));
  }
  puts("N64 decoder fixtures passed.");
}
