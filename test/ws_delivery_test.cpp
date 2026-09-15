#include "ws_delivery.h"
#include <assert.h>
#include <stdio.h>

using Delivery = WsDelivery;
using Attempt = Delivery::Attempt;

static Attempt prepare(Delivery &delivery, uint32_t &now) {
  now += Delivery::IntervalUs;
  Attempt attempt;
  assert(delivery.prepare(now, attempt));
  return attempt;
}

static void acknowledge(Delivery &delivery, const Attempt &attempt) {
  for (size_t i = 0; i < attempt.count; ++i)
    assert(!delivery.complete(attempt, i, true));
}

static void initialSnapshots(Delivery &delivery, uint32_t &now) {
  for (size_t pad = 0; pad < 4; ++pad) {
    auto attempt = prepare(delivery, now);
    assert(attempt.packet[0] == pad);
    acknowledge(delivery, attempt);
  }
  assert(!delivery.pending());
}

int main() {
  Delivery delivery;
  uint32_t now = 0;
  assert(delivery.connect(10));
  assert(delivery.connect(20));
  initialSnapshots(delivery, now);
  const uint8_t pressed[] = {0x80, 0, 0x80, 0x7f};
  delivery.update(2, pressed, UINT64_C(5000000000));
  auto attempt = prepare(delivery, now);
  assert(attempt.count == 2 && attempt.packet[0] == 2);
  const uint8_t timestamp[] = {0x00, 0xf2, 0x05, 0x2a, 0x01, 0, 0, 0};
  assert(sizeof(attempt.packet) == 13);
  assert(memcmp(attempt.packet + 5, timestamp, 8) == 0);
  assert(memcmp(attempt.packet + 1, pressed, 4) == 0);
  assert(!delivery.complete(attempt, 0, true));
  assert(!delivery.complete(attempt, 1, false));
  assert(delivery.pending());
  // The fast client's success must not discard the slow client's final state.
  // No new controller input arrives between the original send and this retry.
  attempt = prepare(delivery, now);
  assert(attempt.count == 1 && attempt.clients[0] == 20);
  assert(memcmp(attempt.packet + 5, timestamp, 8) == 0);
  assert(memcmp(attempt.packet + 1, pressed, 4) == 0);
  acknowledge(delivery, attempt);
  assert(!delivery.pending());

  // A binary() failure uses the same retry rules as a socket that cannot accept writes.
  delivery.update(0, pressed);
  attempt = prepare(delivery, now);
  for (size_t i = 0; i < attempt.count; ++i)
    assert(!delivery.complete(attempt, i, false));
  Attempt tooSoon;
  assert(!delivery.prepare(now, tooSoon));
  assert(!delivery.prepare(now + Delivery::IntervalUs - 1, tooSoon));
  const uint8_t released[] = {0, 0, 0, 0};
  delivery.update(0, released);
  attempt = prepare(delivery, now);
  assert(memcmp(attempt.packet + 1, released, 4) == 0);
  acknowledge(delivery, attempt);

  // Retry initial snapshots. Include state captured with no clients.
  Delivery snapshot;
  uint32_t snapshotTime = 0;
  snapshot.update(0, pressed);
  assert(!snapshot.pending());
  assert(snapshot.connect(1));
  attempt = prepare(snapshot, snapshotTime);
  assert(memcmp(attempt.packet + 1, pressed, 4) == 0);
  assert(!snapshot.complete(attempt, 0, false));
  for (size_t pad = 1; pad < 4; ++pad) {
    attempt = prepare(snapshot, snapshotTime);
    assert(attempt.packet[0] == pad); // Failed sends do not starve other ports.
    acknowledge(snapshot, attempt);
  }
  attempt = prepare(snapshot, snapshotTime);
  assert(attempt.packet[0] == 0);
  acknowledge(snapshot, attempt);
  assert(!snapshot.pending());

  // An acknowledgment must preserve a newer update or reconnect between prepare/complete.
  snapshot.update(0, pressed);
  attempt = prepare(snapshot, snapshotTime);
  snapshot.update(0, released);
  acknowledge(snapshot, attempt);
  assert(snapshot.pending());
  attempt = prepare(snapshot, snapshotTime);
  snapshot.disconnect(1);
  assert(snapshot.connect(1));
  acknowledge(snapshot, attempt);
  for (size_t i = 0; i < 4; ++i) {
    attempt = prepare(snapshot, snapshotTime);
    assert(attempt.count == 1);
    acknowledge(snapshot, attempt);
  }
  assert(!snapshot.pending());

  // Close clients that stay blocked at the exact limit, not on each loop iteration.
  Delivery blocked;
  uint32_t blockedTime = 0;
  assert(blocked.connect(1));
  for (size_t i = 1; i <= Delivery::BlockedLimit; ++i) {
    attempt = prepare(blocked, blockedTime);
    assert(attempt.packet[0] == (i - 1) % 4);
    assert(blocked.complete(attempt, 0, false) == (i == Delivery::BlockedLimit));
  }
  assert(!blocked.pending());
  assert(blocked.connect(1));
  for (size_t i = 1; i < Delivery::BlockedLimit; ++i) {
    attempt = prepare(blocked, blockedTime);
    assert(!blocked.complete(attempt, 0, false));
  }
  attempt = prepare(blocked, blockedTime);
  acknowledge(blocked, attempt); // Successful recovery resets the failure streak.
  attempt = prepare(blocked, blockedTime);
  assert(!blocked.complete(attempt, 0, false));
  blocked.disconnect(1);
  assert(!blocked.pending());

  Delivery capacity;
  for (uint32_t id = 0; id < Delivery::MaxClients; ++id) assert(capacity.connect(id));
  assert(capacity.connect(0)); // Duplicate connect does not consume a slot.
  assert(!capacity.connect(99));
  capacity.disconnect(3);
  assert(capacity.connect(99));

  Delivery rollover;
  assert(rollover.connect(1));
  assert(rollover.prepare(UINT32_MAX - 10000, attempt));
  assert(!rollover.prepare(9998, attempt));
  assert(rollover.prepare(9999, attempt));
  puts("WebSocket delivery regressions passed.");
}
