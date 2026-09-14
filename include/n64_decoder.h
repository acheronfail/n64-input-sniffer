#pragma once

#include <stddef.h>
#include <stdint.h>
#include <string.h>

// Poll byte and stop bit, followed by the 32-bit controller response.
#define N64_PREFIX 9
#define N64_BITCOUNT 32
#define N64_FRAMEBITS (N64_PREFIX + N64_BITCOUNT)
#define N64_POLL_COMMAND 0x01
// Pulse timings in microseconds. The remote control peripheral (RMT) captures at 1us resolution.
#define N64_LOW_ONE_MAX_US 2
#define N64_LOW_MIN_US 1
#define N64_LOW_MAX_US 4
#define N64_CELL_MIN_US 3
#define N64_CELL_MAX_US 6
// Bound temporary capture storage even for long/noisy transactions.
#define RMT_MAX_CAPTURE_BITS 96

/** Decode one byte from the 8 bits of `bits` at `offset`, most significant bit (MSB) first. */
static inline uint8_t readByte(const uint8_t *bits, int offset) {
  uint8_t val = 0;
  for (int i = 0; i < 8; ++i) {
    if (bits[offset + i]) {
      val |= (uint8_t)(1 << (7 - i));
    }
  }
  return val;
}

/** Return true if the 9-bit prefix contains the console's poll command
 * (byte 0x01, MSB-first), then a stop bit (1). */
static inline bool isPollResponse(const uint8_t *frame) {
  const uint8_t command = readByte(frame, 0); // first 8 prefix bits
  const uint8_t stopBit = frame[8];           // 9th prefix bit
  return command == N64_POLL_COMMAND && stopBit == 1;
}

/**
 * The controller does not use response bits 8 and 9. Valid packets must set them to zero.
 * This check rejects many false decodes from random data or noise.
 */
static inline bool hasValidReservedBits(const uint8_t *frame) {
  const uint8_t *r = frame + N64_PREFIX;
  return r[8] == 0 && r[9] == 0;
}

/** Convert a low pulse width in microseconds to an N64 bit value. */
static inline uint8_t decodeBitFromLowUs(uint32_t lowUs) {
  return (lowUs <= N64_LOW_ONE_MAX_US) ? 1U : 0U;
}

/** Check that one low/high pulse pair matches a real N64 bit cell. */
static inline bool isValidN64CellUs(uint32_t lowUs, uint32_t highUs) {
  if (lowUs < N64_LOW_MIN_US || lowUs > N64_LOW_MAX_US) {
    return false;
  }

  uint32_t total = lowUs + highUs;
  return total >= N64_CELL_MIN_US && total <= N64_CELL_MAX_US;
}

/**
 * Decode an RMT packet into an N64 frame (9-bit poll prefix + 32-bit response).
 * Return true if the packet contains a full poll-response frame.
 */
template <typename Item>
static bool decodeFrameFromRmtItems(const Item *items, size_t count,
                                    uint8_t frame[N64_FRAMEBITS]) {
  uint8_t bits[RMT_MAX_CAPTURE_BITS];
  size_t bitCount = 0;

  for (size_t i = 0; i < count && bitCount < RMT_MAX_CAPTURE_BITS; ++i) {
    const Item &item = items[i];

    // Valid N64 traffic goes low->high for each bit cell.
    // Decode only those cells. Ignore malformed segments and noise.
    if (item.level0 == 0 && item.level1 == 1 && item.duration0 > 0 &&
        item.duration1 > 0 &&
        isValidN64CellUs(item.duration0, item.duration1)) {
      bits[bitCount++] = decodeBitFromLowUs(item.duration0);
    }

    if (item.level0 == 1 && item.level1 == 0 && item.duration0 > 0 &&
        item.duration1 > 0 && bitCount < RMT_MAX_CAPTURE_BITS &&
        isValidN64CellUs(item.duration1, item.duration0)) {
      bits[bitCount++] = decodeBitFromLowUs(item.duration1);
    }
  }

  if (bitCount != N64_FRAMEBITS) {
    return false;
  }

  if (!isPollResponse(bits)) {
    return false;
  }

  memcpy(frame, bits, N64_FRAMEBITS);
  return true;
}

/**
 * Pack the 32-bit controller response into 4 bytes for the wire.
 * Each button byte is MSB-first, as in readByte.
 * The bit masks in web/src/lib/controller.ts use the same layout:
 *   [0] A B Z START UP DOWN LEFT RIGHT
 *   [1] - - L R C-UP C-DOWN C-LEFT C-RIGHT   (top 2 bits are the unused 8,9)
 *   [2] stick X (int8)   [3] stick Y (int8)
 */
static void packState(const uint8_t *frame, uint8_t out[4]) {
  const uint8_t *r = frame + N64_PREFIX; // start of the 32-bit response
  out[0] = readByte(r, 0);
  out[1] = readByte(r, 8);
  out[2] = readByte(r, 16);
  out[3] = readByte(r, 24);
}

