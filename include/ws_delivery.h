#pragma once

#include <stddef.h>
#include <stdint.h>
#include <string.h>

// Delivery of the latest state, with separate acknowledgments for each browser.
// Callers serialize access. This class does no network operations.
class WsDelivery {
public:
  static constexpr size_t Controllers = 4;
  static constexpr size_t MaxClients = 8;
  static constexpr uint32_t IntervalUs = 20000;
  static constexpr uint16_t BlockedLimit = 60;
  struct Attempt {
    uint8_t packet[5] = {};
    uint32_t revision = 0;
    uint32_t clients[MaxClients] = {};
    uint32_t sessions[MaxClients] = {};
    size_t count = 0;
  };

  bool connect(uint32_t id) {
    if (find(id)) return true;
    for (auto &client : clients) {
      if (client.active) continue;
      client = Client{};
      client.active = true;
      client.id = id;
      client.session = ++session;
      client.pending = 0x0f; // Initial snapshots use the same retry path.
      return true;
    }
    return false;
  }

  void disconnect(uint32_t id) {
    if (auto *client = find(id)) *client = Client{};
  }

  void update(size_t controller, const uint8_t payload[4]) {
    if (controller >= Controllers) return;
    memcpy(latest[controller], payload, 4);
    ++revisions[controller];
    for (auto &client : clients) {
      if (client.active) client.pending |= uint8_t(1U << controller);
    }
  }

  bool pending() const {
    for (const auto &client : clients)
      if (client.active && client.pending) return true;
    return false;
  }

  bool prepare(uint32_t nowUs, Attempt &attempt) {
    attempt = Attempt{};
    if (uint32_t(nowUs - lastAttemptUs) < IntervalUs) return false;
    for (size_t offset = 0; offset < Controllers; ++offset) {
      const size_t controller = (nextController + offset) % Controllers;
      for (const auto &client : clients) {
        if (!client.active || !(client.pending & (1U << controller))) continue;
        attempt.clients[attempt.count] = client.id;
        attempt.sessions[attempt.count++] = client.session;
      }
      if (!attempt.count) continue;
      attempt.packet[0] = uint8_t(controller);
      memcpy(attempt.packet + 1, latest[controller], 4);
      attempt.revision = revisions[controller];
      // Limit the retry rate after failures too. Advance even if every client is blocked.
      lastAttemptUs = nowUs;
      nextController = (controller + 1) % Controllers;
      return true;
    }
    return false;
  }

  // Return true when the caller must close a client that stays blocked.
  bool complete(const Attempt &attempt, size_t recipient, bool sent) {
    if (recipient >= attempt.count) return false;
    auto *client = find(attempt.clients[recipient]);
    if (!client || client->session != attempt.sessions[recipient]) return false;
    if (sent) {
      client->blocked = 0;
      const size_t controller = attempt.packet[0];
      if (revisions[controller] == attempt.revision)
        client->pending &= uint8_t(~(1U << controller));
    } else if (++client->blocked >= BlockedLimit) {
      *client = Client{};
      return true;
    }
    return false;
  }

private:
  struct Client {
    uint32_t id = 0;
    uint32_t session = 0;
    uint16_t blocked = 0;
    uint8_t pending = 0;
    bool active = false;
  };
  Client clients[MaxClients] = {};
  uint8_t latest[Controllers][4] = {};
  uint32_t revisions[Controllers] = {};
  uint32_t lastAttemptUs = 0;
  uint32_t session = 0;
  size_t nextController = 0;

  Client *find(uint32_t id) {
    for (auto &client : clients)
      if (client.active && client.id == id) return &client;
    return nullptr;
  }
};
