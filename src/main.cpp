/**
 * Ported to ESP32 from NintendoSpy N64.
 *
 * This passive bus sniffer reads the single data wire between an N64 console
 * and a controller. It decodes the controller's response to the console's poll
 * command (0x01). The ESP32 only reads the line. It never drives the line.
 *
 * Each N64 bit is a ~4us pulse on an open-collector line that stays high when idle.
 * A '0' is low for ~3us and high for ~1us.
 * A '1' is low for ~1us and high for ~3us.
 * The ESP32's remote control peripheral (RMT) timestamps received pulse widths
 * in hardware. The firmware decodes each bit from the low pulse duration.
 *
 * Each polled frame starts with the console's 9-bit prefix: the 0x01 command
 * byte 0000_0001 and a stop bit, giving 0000_0001 1.
 * The controller's 32-bit response comes immediately after the prefix.
 */

#include <Arduino.h>
#include <atomic>
#include <ArduinoOTA.h>
#include <ESPAsyncWebServer.h>
#include <ESPmDNS.h>
#include <Preferences.h>
#include <WiFi.h>
#include <WiFiManager.h>
#include <driver/rmt.h>
#include <freertos/ringbuf.h>

#include "web_ui.h"
#include "controller_commands.h"
#include "wifi_status_led.h"
#include "n64_decoder.h"
#include "ws_delivery.h"

static ControllerCommands controllerCommands;
static std::atomic<bool> powerLedEnabled{true};
static std::atomic<bool> wifiLedConnected{false};
static std::atomic<bool> wifiLedPortal{false};
static std::atomic<uint32_t> wifiLedFailures{0};
static std::atomic<ControllerCommands::Led> commandLed{ControllerCommands::Led::Normal};
static void processCommandFrame(size_t controller, const uint8_t *frame);

// ---------- WiFi / setup portal ---------------------------------------------
// The firmware contains no fixed credentials. On first boot or after a failed
// reconnect, the ESP32 starts an open access point (AP) named AP_NAME.
// Join it from a phone or laptop. Select your network in the captive portal.
// Enter the password. WiFiManager saves it in flash.
// The ESP32 reconnects automatically on later boots.
//
// Hold BOOT (WIFI_RESET_PIN) for WIFI_RESET_HOLD_MS to delete the saved network
// and reboot into the setup portal. This applies at startup or during normal operation.
#define AP_NAME "N64Spy-Setup"
#define MDNS_HOST "n64spy"
#define WIFI_RESET_PIN 0       // BOOT button on most ESP32 dev boards
#define WIFI_RESET_HOLD_MS 3000 // hold duration to delete WiFi credentials and restart

// ---------- Over-the-air updates --------------------------------------------
// After connection, the ESP32 accepts firmware uploads over WiFi without USB.
// PlatformIO command: `pio run -e esp32dev_ota -t upload`.
// The device advertises OTA_HOSTNAME.local through multicast DNS (mDNS).
// Set upload_port to that name or its IP address in platformio.ini.
//
// OTA_PASSWORD controls authentication for over-the-air (OTA) updates.
// Leave it empty to disable authentication.
// For a password, set OTA_PASSWORD. Pass --auth=<password> through upload_flags in platformio.ini.
#define OTA_HOSTNAME MDNS_HOST
#define OTA_PASSWORD ""

// ---------- Wiring -----------------------------------------------------------
// Connect this GPIO to the N64 controller DATA line, the middle pin of the 3-pin N64 connector.
// The N64 data line uses 3.3V logic with a pull-up on the console side.
// It connects directly to an ESP32 input pin without level shifting.
// Share a common ground with the console/controller.
//
// Up to 4 controller data lines, one per RMT RX channel.
#define N64_CONTROLLER_COUNT 4
#define N64_PIN_1 13
#define N64_PIN_2 12
#define N64_PIN_3 11
#define N64_PIN_4 10

#define SERIAL_BAUD 115200

// Maximum time loop() waits for a frame with interrupts enabled before it returns.
// This limit lets the interrupt watchdog and real-time operating system (RTOS)
// run when the line is idle or no console is attached.
#define FRAME_WAIT_US 5000

// End RMT reception after the bus stays at one level for this duration.
#define RMT_IDLE_THRESHOLD_US 12

// On ESP32-S3 with the legacy RMT API, channels 4-7 are RX-capable.
static constexpr int kN64Pins[N64_CONTROLLER_COUNT] = {
  N64_PIN_1, N64_PIN_2, N64_PIN_3, N64_PIN_4};
static constexpr rmt_channel_t kN64Channels[N64_CONTROLLER_COUNT] = {
  RMT_CHANNEL_4, RMT_CHANNEL_5, RMT_CHANNEL_6, RMT_CHANNEL_7};
static RingbufHandle_t n64RmtRingbufs[N64_CONTROLLER_COUNT] = {nullptr, nullptr,
                                 nullptr, nullptr};

// The HTTP server serves the user interface (UI), which listens to the WebSocket.
// Both run in the AsyncTCP task on the other core and do not block pulse capture.
static AsyncWebServer server(80);
static AsyncWebSocket ws("/ws");

// Last captured state per controller, for change detection and serial logging.
// WsDelivery owns a separate snapshot for browser delivery.
static uint8_t lastPayload[N64_CONTROLLER_COUNT][4] = {
  {0, 0, 0, 0}, {0, 0, 0, 0}, {0, 0, 0, 0}, {0, 0, 0, 0}};
static WsDelivery wsDelivery;
static portMUX_TYPE wsDeliveryMux = portMUX_INITIALIZER_UNLOCKED;
static uint32_t wsDiscardCount = 0;
static uint32_t wsDisconnectCount = 0;
static uint32_t wsSlowCloseCount = 0;
static uint32_t wifiDisconnectCount = 0;
static uint32_t lastWsDiagAtMs = 0;

// A port is "connected" if it recently received valid poll-response frames.
// This detects activity, not the cable connection itself.
#define PORT_ACTIVITY_TIMEOUT_MS 1500
#define PORT_PROBE_INTERVAL_MS 100
#define PORT_PROBE_WINDOW_MS 30
static bool controllerConnected[N64_CONTROLLER_COUNT] = {false, false, false,
                                                         false};
static uint32_t controllerLastSeenMs[N64_CONTROLLER_COUNT] = {0, 0, 0, 0};
static bool controllerRxRunning[N64_CONTROLLER_COUNT] = {false, false, false,
                                                         false};
static bool controllerProbing[N64_CONTROLLER_COUNT] = {false, false, false,
                                                       false};
static uint32_t controllerProbeStartedMs[N64_CONTROLLER_COUNT] = {0, 0, 0, 0};
static uint32_t controllerLastProbeAtMs[N64_CONTROLLER_COUNT] = {0, 0, 0, 0};

/** Configure one controller's RMT RX channel for 1us pulse capture. */
static bool startRmtCapture(size_t controller) {
  if (controller >= N64_CONTROLLER_COUNT) {
    return false;
  }

  rmt_config_t cfg = {};
  cfg.rmt_mode = RMT_MODE_RX;
  cfg.channel = kN64Channels[controller];
  cfg.gpio_num = (gpio_num_t)kN64Pins[controller];
  cfg.clk_div = 80; // 80MHz APB / 80 = 1MHz tick => 1us resolution.
  // ESP32-S3 legacy RMT limits memory per group.
  // With 4 receive (RX) channels active, use one block per channel to configure all channels.
  cfg.mem_block_num = 1;
  cfg.flags = 0;
  cfg.rx_config.idle_threshold = RMT_IDLE_THRESHOLD_US;
  // Remove glitches shorter than one microsecond before they reach the RX ring buffer.
  cfg.rx_config.filter_en = true;
  cfg.rx_config.filter_ticks_thresh = 1;

  esp_err_t err = rmt_config(&cfg);
  if (err != ESP_OK) {
    Serial.printf("RMT config failed (pad %u): %d\n", (unsigned)(controller + 1),
                  (int)err);
    return false;
  }

  err = rmt_driver_install(kN64Channels[controller], 4096, 0);
  if (err != ESP_OK) {
    Serial.printf("RMT driver install failed (pad %u): %d\n",
                  (unsigned)(controller + 1), (int)err);
    return false;
  }

  err = rmt_get_ringbuf_handle(kN64Channels[controller],
                               &n64RmtRingbufs[controller]);
  if (err != ESP_OK || n64RmtRingbufs[controller] == nullptr) {
    Serial.printf("RMT ringbuf setup failed (pad %u): %d\n",
                  (unsigned)(controller + 1), (int)err);
    return false;
  }

  controllerRxRunning[controller] = false;
  controllerProbing[controller] = false;
  return true;
}

static bool startControllerRx(size_t controller) {
  if (controller >= N64_CONTROLLER_COUNT) {
    return false;
  }
  if (controllerRxRunning[controller]) {
    return true;
  }

  esp_err_t err = rmt_rx_start(kN64Channels[controller], true);
  if (err != ESP_OK) {
    Serial.printf("RMT RX start failed (pad %u): %d\n",
                  (unsigned)(controller + 1),
                  (int)err);
    return false;
  }

  controllerRxRunning[controller] = true;
  return true;
}

static void stopControllerRx(size_t controller) {
  if (controller >= N64_CONTROLLER_COUNT || !controllerRxRunning[controller]) {
    return;
  }

  esp_err_t err = rmt_rx_stop(kN64Channels[controller]);
  if (err != ESP_OK) {
    Serial.printf("RMT RX stop failed (pad %u): %d\n", (unsigned)(controller + 1),
                  (int)err);
  }
  controllerRxRunning[controller] = false;
}

/** Poll one controller's RMT ring buffer and decode one N64 frame if present. */
static bool readFrameFromRmt(size_t controller, uint8_t frame[N64_FRAMEBITS]) {
  if (controller >= N64_CONTROLLER_COUNT || n64RmtRingbufs[controller] == nullptr) {
    return false;
  }

  bool foundFrame = false;

  for (;;) {
    size_t rxSize = 0;
    rmt_item32_t *items = (rmt_item32_t *)xRingbufferReceive(
        n64RmtRingbufs[controller], &rxSize, 0);
    if (items == nullptr) {
      break;
    }

    if (rxSize >= sizeof(rmt_item32_t)) {
      uint8_t latestFrame[N64_FRAMEBITS];
      if (decodeFrameFromRmtItems(items, rxSize / sizeof(rmt_item32_t),
                                  latestFrame)) {
        // Process every queued frame so emptying the queue does not hide button edges.
        processCommandFrame(controller, latestFrame);
        memcpy(frame, latestFrame, N64_FRAMEBITS);
        foundFrame = true;
      }
    }

    vRingbufferReturnItem(n64RmtRingbufs[controller], (void *)items);
  }

  return foundFrame;
}

/** Decoded N64 controller state. */
struct N64State {
  bool a, b, z, start;
  bool up, down, left, right;
  bool l, r;
  bool cUp, cDown, cLeft, cRight;
  int8_t stickX;
  int8_t stickY;
};

/**
 * Bit positions in the 32-bit controller response match NintendoSpy's
 * Readers/Nintendo64.cs. The controller does not use indices 8 and 9.
 */
enum N64ResponseBit {
  RESP_A = 0,
  RESP_B,
  RESP_Z,
  RESP_START,
  RESP_UP,
  RESP_DOWN,
  RESP_LEFT,
  RESP_RIGHT,
  RESP_L = 10,
  RESP_R,
  RESP_C_UP,
  RESP_C_DOWN,
  RESP_C_LEFT,
  RESP_C_RIGHT,
  RESP_STICK_X = 16, // 8-bit signed, MSB-first
  RESP_STICK_Y = 24, // 8-bit signed, MSB-first
};

/** Decode the controller response that follows the prefix in `frame`. */
static N64State decodeState(const uint8_t *frame) {
  const uint8_t *r = frame + N64_PREFIX; // start of the 32-bit response
  N64State s;
  s.a = r[RESP_A];
  s.b = r[RESP_B];
  s.z = r[RESP_Z];
  s.start = r[RESP_START];
  s.up = r[RESP_UP];
  s.down = r[RESP_DOWN];
  s.left = r[RESP_LEFT];
  s.right = r[RESP_RIGHT];
  s.l = r[RESP_L];
  s.r = r[RESP_R];
  s.cUp = r[RESP_C_UP];
  s.cDown = r[RESP_C_DOWN];
  s.cLeft = r[RESP_C_LEFT];
  s.cRight = r[RESP_C_RIGHT];
  s.stickX = (int8_t)readByte(r, RESP_STICK_X);
  s.stickY = (int8_t)readByte(r, RESP_STICK_Y);
  return s;
}

/** Print one controller's state over serial in a readable format. */
static void printState(size_t controller, const N64State &s) {
  char buf[160];
  int n = 0;
  n += snprintf(buf + n, sizeof(buf) - n, "[N64 %u]",
                (unsigned)(controller + 1));

#define BTN(label, field)                                                      \
  do {                                                                         \
    if (s.field)                                                               \
      n += snprintf(buf + n, sizeof(buf) - n, " " label);                      \
  } while (0)
  BTN("A", a);
  BTN("B", b);
  BTN("Z", z);
  BTN("START", start);
  BTN("UP", up);
  BTN("DOWN", down);
  BTN("LEFT", left);
  BTN("RIGHT", right);
  BTN("L", l);
  BTN("R", r);
  BTN("C-UP", cUp);
  BTN("C-DOWN", cDown);
  BTN("C-LEFT", cLeft);
  BTN("C-RIGHT", cRight);
#undef BTN

  n += snprintf(buf + n, sizeof(buf) - n, "  stick=(%d, %d)", s.stickX,
                s.stickY);
  Serial.println(buf);
}

static bool anyPendingPackets() {
  portENTER_CRITICAL(&wsDeliveryMux);
  const bool pending = wsDelivery.pending();
  portEXIT_CRITICAL(&wsDeliveryMux);
  return pending;
}

/** Retry the latest state independently for each client at a bounded rate. */
static void flushPendingPayload() {
  WsDelivery::Attempt attempt;
  portENTER_CRITICAL(&wsDeliveryMux);
  const bool ready = wsDelivery.prepare(micros(), attempt);
  portEXIT_CRITICAL(&wsDeliveryMux);
  if (!ready) return;

  // Network calls stay outside the lock shared with AsyncTCP callbacks.
  for (size_t i = 0; i < attempt.count; ++i) {
    const uint32_t id = attempt.clients[i];
    if (!ws.hasClient(id)) {
      portENTER_CRITICAL(&wsDeliveryMux);
      wsDelivery.disconnect(id);
      portEXIT_CRITICAL(&wsDeliveryMux);
      continue;
    }
    bool sent = false;
    if (ws.availableForWrite(id)) {
      sent = ws.binary(id, attempt.packet, sizeof(attempt.packet));
      if (!sent) ++wsDiscardCount;
    }
    portENTER_CRITICAL(&wsDeliveryMux);
    const bool close = wsDelivery.complete(attempt, i, sent);
    portEXIT_CRITICAL(&wsDeliveryMux);
    if (close) {
      Serial.printf("[ws] closing slow client id=%lu\n", (unsigned long)id);
      ws.close(id, 1013, "server busy");
      ++wsSlowCloseCount;
    }
  }
}

/** Summarize WebSocket/WiFi status at intervals to limit serial output. */
static void logWsDiagnostics() {
  uint32_t nowMs = millis();
  if (nowMs - lastWsDiagAtMs < 1000) {
    return;
  }

  lastWsDiagAtMs = nowMs;
  if (wsDiscardCount == 0 && wsDisconnectCount == 0 && wsSlowCloseCount == 0 &&
      wifiDisconnectCount == 0) {
    return;
  }

  Serial.printf("[ws] clients=%u pending=%u discards=%lu ws_disc=%lu slow_close=%lu wifi_disc=%lu\n",
                (unsigned)ws.count(), anyPendingPackets() ? 1U : 0U,
                (unsigned long)wsDiscardCount,
                (unsigned long)wsDisconnectCount,
                (unsigned long)wsSlowCloseCount,
                (unsigned long)wifiDisconnectCount);
  wsDiscardCount = 0;
  wsDisconnectCount = 0;
  wsSlowCloseCount = 0;
  wifiDisconnectCount = 0;
}

/** Update per-port connected/disconnected state from recent frame activity. */
static void refreshControllerConnectionState() {
  uint32_t nowMs = millis();

  for (size_t controller = 0; controller < N64_CONTROLLER_COUNT; ++controller) {
    if (!controllerConnected[controller]) {
      continue;
    }

    if ((uint32_t)(nowMs - controllerLastSeenMs[controller]) <=
        PORT_ACTIVITY_TIMEOUT_MS) {
      continue;
    }

    controllerConnected[controller] = false;
    controllerProbing[controller] = false;
    stopControllerRx(controller);
    Serial.printf("[port %u] disconnected (no poll traffic)\n",
                  (unsigned)(controller + 1));
  }
}

/**
 * Probe disconnected ports automatically. Keep RX stopped most of the time.
 * Use short probe windows to find controller lines with new activity.
 */
static void serviceControllerProbing() {
  uint32_t nowMs = millis();

  for (size_t controller = 0; controller < N64_CONTROLLER_COUNT; ++controller) {
    if (controllerConnected[controller]) {
      if (!controllerRxRunning[controller]) {
        startControllerRx(controller);
      }
      continue;
    }

    if (!controllerRxRunning[controller]) {
      if ((uint32_t)(nowMs - controllerLastProbeAtMs[controller]) <
          PORT_PROBE_INTERVAL_MS) {
        continue;
      }

      if (startControllerRx(controller)) {
        controllerProbing[controller] = true;
        controllerProbeStartedMs[controller] = nowMs;
        controllerLastProbeAtMs[controller] = nowMs;
      }
      continue;
    }

    if (controllerProbing[controller] &&
        (uint32_t)(nowMs - controllerProbeStartedMs[controller]) >=
            PORT_PROBE_WINDOW_MS) {
      controllerProbing[controller] = false;
      stopControllerRx(controller);
    }
  }
}

/** Queue initial snapshots through the same retry path as live updates. */
static void onWsEvent(AsyncWebSocket *server, AsyncWebSocketClient *client,
                      AwsEventType type, void *arg, uint8_t *data, size_t len) {
  if (type == WS_EVT_CONNECT) {
    client->setCloseClientOnQueueFull(false);
    portENTER_CRITICAL(&wsDeliveryMux);
    const bool tracked = wsDelivery.connect(client->id());
    portEXIT_CRITICAL(&wsDeliveryMux);
    if (!tracked) {
      Serial.printf("[ws] too many tracked clients; closing id=%lu\n",
                    (unsigned long)client->id());
      ws.close(client->id(), 1008, "too many clients");
      return;
    }
    Serial.printf("[ws] connect id=%lu from=%s\n", (unsigned long)client->id(),
                  client->remoteIP().toString().c_str());
  } else if (type == WS_EVT_DISCONNECT) {
    portENTER_CRITICAL(&wsDeliveryMux);
    wsDelivery.disconnect(client->id());
    portEXIT_CRITICAL(&wsDeliveryMux);
    ++wsDisconnectCount;
    Serial.printf("[ws] disconnect id=%lu from=%s\n",
                  (unsigned long)client->id(),
                  client->remoteIP().toString().c_str());
  }
}

/** Log WiFi link changes to compare their timing with browser disconnections. */
static void onWiFiEvent(WiFiEvent_t event, arduino_event_info_t info) {
  if (event == ARDUINO_EVENT_WIFI_STA_GOT_IP) {
    wifiLedConnected.store(true);
    Serial.printf("[wifi] got ip=%s\n", WiFi.localIP().toString().c_str());
  } else if (event == ARDUINO_EVENT_WIFI_STA_DISCONNECTED) {
    wifiLedConnected.store(false);
    // WiFiManager deliberately disconnects while changing credentials.
    if (info.wifi_sta_disconnected.reason != WIFI_REASON_ASSOC_LEAVE) {
      wifiLedFailures.fetch_add(1);
    }
    ++wifiDisconnectCount;
    Serial.printf("[wifi] disconnected reason=%d\n",
                  info.wifi_sta_disconnected.reason);
  }
}

/**
 * Start the ArduinoOTA listener for firmware uploads over WiFi.
 * mDNS already runs when this function starts. OTA adds its service to the existing responder.
 * The handlers below only log progress. The library writes the firmware and reboots.
 */
static void startOTA() {
  ArduinoOTA.setHostname(OTA_HOSTNAME);
  if (strlen(OTA_PASSWORD) > 0) {
    ArduinoOTA.setPassword(OTA_PASSWORD);
  }

  ArduinoOTA.onStart([]() {
    Serial.println("OTA update starting -- pausing controller sniffing.");
  });
  ArduinoOTA.onEnd([]() { Serial.println("\nOTA update complete; rebooting."); });
  ArduinoOTA.onProgress([](unsigned int done, unsigned int total) {
    Serial.printf("OTA progress: %u%%\r", (done * 100) / total);
  });
  ArduinoOTA.onError([](ota_error_t error) {
    Serial.printf("OTA error [%u]\n", error);
  });

  ArduinoOTA.begin();
  Serial.printf("OTA ready -- flash to %s.local\n", OTA_HOSTNAME);
}

/** Erase the saved WiFi network and reboot (into the setup portal). */
static void clearWiFiAndRestart() {
  Serial.println("Erasing saved WiFi and restarting into setup portal...");
  WiFiManager wm;
  wm.resetSettings();
  delay(200); // let the serial output finish
  ESP.restart();
}

static void setStatusLed(uint32_t color);

/**
 * Start WiFi through the captive setup portal, then start mDNS and the web server.
 * Wait in setup() until connected, or restart if the portal times out.
 * The asynchronous server starts afterward, so it does not compete with WiFiManager's server.
 */
static void startNetwork() {
  WiFi.mode(WIFI_STA);
  // Disable modem sleep to reduce latency, jitter, and WebSocket interruptions during sustained traffic.
  WiFi.setSleep(false);
  WiFi.onEvent(onWiFiEvent);

  WiFiManager wm;
  pinMode(WIFI_RESET_PIN, INPUT_PULLUP);
  if (digitalRead(WIFI_RESET_PIN) == LOW) {
    Serial.println("BOOT held -- forgetting saved WiFi, opening setup portal.");
    wm.resetSettings();
  }

  // The captive portal runs its own synchronous WebServer on port 80.
  // It does not release the socket in time for AsyncWebServer during the same boot.
  // If the portal runs, reboot after it saves credentials.
  // The next boot connects directly without the portal, so port 80 stays available.
  bool justConfigured = false;
  wm.setSaveConfigCallback([&]() { justConfigured = true; });
  wm.setAPCallback([](WiFiManager *) { wifiLedPortal.store(true); });
  wm.setPreSaveConfigCallback([]() { wifiLedPortal.store(false); });

  // Try saved credentials. If they fail, open the captive portal for new credentials.
  // Restart on timeout so a brief router outage leads to another attempt on the next boot.
  wm.setConfigPortalTimeout(180);
  // Process the portal here so the LED can flash while the portal waits.
  // Stay in setup until connected: controller commands still require WiFi.
  wm.setConfigPortalBlocking(false);
  Serial.printf("Joining WiFi (or open the \"%s\" network to configure)...\n",
                AP_NAME);
  bool connected = wm.autoConnect(AP_NAME);
  while (!connected && wm.getConfigPortalActive()) {
    connected = wm.process();
    // process() tries the submitted credentials.
    // The pre-save callback selects blue until process() returns. Failed attempts return to red.
    wifiLedPortal.store(!connected && wm.getConfigPortalActive());
    delay(1);
  }
  if (!connected) {
    Serial.println("WiFi setup timed out; restarting.");
    wifiLedConnected.store(false);
    wifiLedFailures.fetch_add(1);
    delay(WiFiStatusLed::FailureMs + 50);
    ESP.restart();
  }

  wifiLedConnected.store(true);
  wifiLedPortal.store(false);

  if (justConfigured) {
    Serial.println("WiFi saved -- rebooting to start the web server cleanly.");
    delay(WiFiStatusLed::SuccessMs + 50);
    ESP.restart();
  }

  Serial.printf("Connected. Open http://%s/", WiFi.localIP().toString().c_str());
  if (MDNS.begin(MDNS_HOST)) {
    MDNS.addService("http", "tcp", 80);
    Serial.printf(" or http://%s.local/", MDNS_HOST);
  }
  Serial.println();

  ws.onEvent(onWsEvent);
  server.addHandler(&ws);
  // Qualify the enum because WiFiManager includes the WebServer library.
  // That library also defines HTTP_GET, so the bare name is ambiguous here.
  server.on("/", WebRequestMethod::HTTP_GET, [](AsyncWebServerRequest *req) {
    req->send(200, "text/html", INDEX_HTML);
  });
  server.begin();

  startOTA();
}

/** Latch a WS2812 color. Then release the LED's RMT transmit (TX) resources. */
static void setStatusLed(uint32_t color) {
#ifdef POWER_LED_PIN
  static uint32_t lastColor = UINT32_MAX;
  if (lastColor == color) return;
  // Use the same legacy RMT driver as capture to avoid Arduino's separate RMT allocator.
  // S3 channel 0 supports TX. Capture uses RX 4-7.
  rmt_config_t cfg = RMT_DEFAULT_CONFIG_TX((gpio_num_t)POWER_LED_PIN,
                                           RMT_CHANNEL_0);
  cfg.clk_div = 8; // 80 MHz / 8 = 100 ns per tick.
  esp_err_t err = rmt_config(&cfg);
  if (err == ESP_OK) {
    err = rmt_driver_install(cfg.channel, 0, 0);
  }
  if (err != ESP_OK) {
    Serial.printf("Power LED init failed: %d\n", (int)err);
    return;
  }

  // WS2812 sends green, red, blue, MSB first.
  rmt_item32_t bits[24] = {};
  for (size_t i = 0; i < 24; ++i) {
    bool one = (color & (1UL << (23 - i))) != 0;
    bits[i].level0 = 1;
    bits[i].duration0 = one ? 8 : 4;
    bits[i].level1 = 0;
    bits[i].duration1 = one ? 4 : 8;
  }
  err = rmt_write_items(cfg.channel, bits, 24, true);
  delayMicroseconds(300); // Idle low latches the color, which persists.
  rmt_driver_uninstall(cfg.channel);
  if (err != ESP_OK) {
    Serial.printf("Power LED write failed: %d\n", (int)err);
  } else {
    lastColor = color;
  }
#endif
}

// One writer owns the LED/RMT channel.
// WiFi callbacks and the main loop publish atomic inputs.
// Neither waits for a flash sequence to finish.
static void statusLedTask(void *) {
  WiFiStatusLed status;
  for (;;) {
    setStatusLed(status.color(millis(), wifiLedConnected.load(),
                             wifiLedPortal.load(), wifiLedFailures.load(),
                             powerLedEnabled.load(), commandLed.load()));
    vTaskDelay(pdMS_TO_TICKS(10));
  }
}

static void processCommandFrame(size_t controller, const uint8_t *frame) {
  if (!hasValidReservedBits(frame)) return;
  const uint8_t *response = frame + N64_PREFIX;
  const uint16_t buttons = (uint16_t(readByte(response, 0)) << 8) |
                          readByte(response, 8);
  controllerCommands.input(controller, buttons, millis());
}

static void serviceCommands() {
  const uint32_t now = millis();
  const ControllerCommands::Action action = controllerCommands.tick(now);
  if (action == ControllerCommands::Action::ResetWiFi) {
    clearWiFiAndRestart();
  } else if (action == ControllerCommands::Action::TogglePowerLed) {
    powerLedEnabled = !powerLedEnabled;
    Preferences preferences;
    if (preferences.begin("n64spy", false)) {
      if (preferences.putBool("power-led", powerLedEnabled) == 0) {
        Serial.println("Failed to save power LED preference.");
      }
      preferences.end();
    } else {
      Serial.println("Failed to open power LED preferences.");
    }
    Serial.printf("Power LED %s\n", powerLedEnabled ? "enabled" : "disabled");
  }

  commandLed.store(controllerCommands.led(now));
}

/** One-time init: power LED, serial, input pins, and a startup banner. */
void setup() {
  Serial.begin(SERIAL_BAUD);
  Preferences preferences;
  if (preferences.begin("n64spy", true)) {
    powerLedEnabled = preferences.getBool("power-led", true);
    preferences.end();
  }
  setStatusLed(powerLedEnabled ? 0x00FF00 : 0);

  // The N64 line has a pull-up on the console side.
  // Enable the weak internal pull-up too, so disconnected pins read high instead of floating.
  // This gives a clear "no activity" state without noise.
  for (size_t i = 0; i < N64_CONTROLLER_COUNT; ++i) {
    pinMode(kN64Pins[i], INPUT_PULLUP);
  }

  delay(50);
  Serial.println();

  Serial.printf("NintendoSpy N64 reader (ESP32) ready @ %lu MHz\n",
                (unsigned long)(F_CPU / 1000000UL));

  for (size_t i = 0; i < N64_CONTROLLER_COUNT; ++i) {
    Serial.printf("pad %u: GPIO %d via RMT channel %d\n", (unsigned)(i + 1),
                  kN64Pins[i], (int)kN64Channels[i]);
    if (!startRmtCapture(i)) {
      Serial.printf("RMT capture init failed for pad %u; restarting in 2s...\n",
                    (unsigned)(i + 1));
      delay(2000);
      ESP.restart();
    }
  }

  Serial.println(
      "Sniffing up to 4 N64 controller data lines... press buttons to see input.");

  // Start after capture initialization to give this task sole use of LED RMT.
  // This includes WiFiManager's blocking connection calls.
  if (xTaskCreate(statusLedTask, "status-led", 3072, nullptr, 1, nullptr) != pdPASS) {
    Serial.println("Status LED task creation failed; restarting.");
    delay(1000);
    ESP.restart();
  }
  startNetwork();
}

/**
 * If BOOT stays down for WIFI_RESET_HOLD_MS, delete WiFi credentials and reboot.
 * Each loop iteration polls the button, even when the console is idle.
 * millis() measures the hold across calls without a blocking wait.
 */
static void checkResetButton() {
  static uint32_t pressedAt = 0;
  if (digitalRead(WIFI_RESET_PIN) == LOW) {
    if (pressedAt == 0) {
      pressedAt = millis();
    } else if (millis() - pressedAt >= WIFI_RESET_HOLD_MS) {
      clearWiFiAndRestart();
    }
  } else {
    pressedAt = 0; // button released before the hold completed. Reset the timer.
  }
}

/** Read and decode one frame from the wire. Log the state if it changes.
 */
void loop() {
  checkResetButton();
  serviceCommands();
  // Process any active OTA upload. This takes little time when idle.
  // An actual upload blocks here for a few seconds. Capture pauses, then the device reboots.
  ArduinoOTA.handle();
  flushPendingPayload();
  logWsDiagnostics();
  refreshControllerConnectionState();
  serviceControllerProbing();

#ifdef DEBUG_HEARTBEAT
  // Build with `-D DEBUG_HEARTBEAT` to check that the loop runs without console polls.
  // Otherwise, serial stays silent until a button changes.
  // Limit the heartbeat rate to keep other output readable.
  static uint32_t lastBeat = 0;
  if (millis() - lastBeat > 2000) {
    Serial.println("[idle] loop alive, waiting for N64 poll...");
    lastBeat = millis();
  }
#endif

  // Remove disconnected WebSocket clients at a limited rate. This takes little time when idle.
  static uint32_t lastCleanup = 0;
  if (millis() - lastCleanup > 1000) {
    ws.cleanupClients();
    lastCleanup = millis();
  }

  for (size_t controller = 0; controller < N64_CONTROLLER_COUNT; ++controller) {
    uint8_t frame[N64_FRAMEBITS];
    if (!readFrameFromRmt(controller, frame)) {
      continue;
    }
    if (!hasValidReservedBits(frame)) {
      continue;
    }

    uint8_t payload[4];
    packState(frame, payload);

    // Broadcast (and log) only on change per controller.
    if (memcmp(lastPayload[controller], payload, sizeof(payload)) != 0) {
      memcpy(lastPayload[controller], payload, sizeof(payload));
      portENTER_CRITICAL(&wsDeliveryMux);
      wsDelivery.update(controller, payload);
      portEXIT_CRITICAL(&wsDeliveryMux);
      printState(controller, decodeState(frame));
    }

    uint32_t nowMs = millis();
    controllerLastSeenMs[controller] = nowMs;
    if (!controllerConnected[controller]) {
      controllerConnected[controller] = true;
      controllerProbing[controller] = false;
      Serial.printf("[port %u] connected (poll traffic detected)\n",
                    (unsigned)(controller + 1));
    }
  }

  flushPendingPayload();
}
