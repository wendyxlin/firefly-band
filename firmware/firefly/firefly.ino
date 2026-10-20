/*
  Firefly band firmware — Seeed XIAO nRF52840 + Wio-SX1262
  ---------------------------------------------------------
  Board package : Seeed nRF52 Boards (Arduino IDE → Boards Manager), board "Seeed XIAO nRF52840"
  Libraries     : RadioLib (jgromes), Adafruit NeoPixel. Bluefruit (BLE) ships with the board package.
  Status        : prototype code written against the wiring in hardware/wiring.md. Not yet run on hardware.

  What it does
   - Button 1 (Find):   1x finding mode (BLE RSSI → vibration pulse + LED count), 2x "come find me", hold "I'm okay"
   - Button 2 (Safety): 1x discreet help, 2x cancel, hold 3 s SOS
   - Both buttons 5 s:  leave the group.  Button 1 held 5 s at boot window: pairing / join group
   - LoRa (915 MHz):    band ↔ band messages, 12-byte packets with a truncated keyed hash
   - BLE peripheral:    GATT service the iOS app connects to (UUIDs match ios/Firefly/FireflyProtocol.swift)
   - BLE advertising:   1 s beacon so other bands can measure distance by RSSI
*/
#include <RadioLib.h>
#include <Adafruit_NeoPixel.h>
#include <bluefruit.h>

// ---------- Pins (see hardware/wiring.md) ----------
#define PIN_LORA_NSS   D4
#define PIN_LORA_DIO1  D1
#define PIN_LORA_RST   D2
#define PIN_LORA_BUSY  D3
#define PIN_RF_SW      D5
#define PIN_BUTTONS    A0     // resistor ladder: idle ~3.3 V, B2 ~2.0 V, B1 ~0.8 V, both ~0.7 V
#define PIN_MOTOR      D6     // MOSFET gate
#define PIN_LEDS       D7     // SK6812 data
#define NUM_LEDS       4

// ---------- Radio settings (US 915 MHz ISM; use 868.0 in the EU) ----------
const float   LORA_FREQ = 915.0, LORA_BW = 125.0, TCXO_V = 1.6;
const uint8_t LORA_SF = 9, LORA_CR = 7, LORA_SYNC = 0x12;
const int8_t  LORA_DBM = 20;

// ---------- Protocol ----------
enum MsgType : uint8_t { CHECKIN = 1, COME_FIND = 2, HELP = 3, SOS = 4, CANCEL = 5, PING = 6, LEAVE = 7, ASK_CHECKIN = 8, JOIN = 9 };
struct __attribute__((packed)) Packet {
  uint8_t  magic;   // 0xF1
  uint8_t  type;
  uint8_t  from;
  uint8_t  hops;
  uint16_t seq;
  uint8_t  battery;
  int8_t   rssi;
  uint32_t mac;
};
static_assert(sizeof(Packet) == 12, "packet must be 12 bytes");

// GATT (must match the app)
BLEService        ffService("F1F1A000-7C3B-4E2A-9A1D-5B0E46F1F1F1");
BLECharacteristic ffEvents ("F1F1A001-7C3B-4E2A-9A1D-5B0E46F1F1F1");
BLECharacteristic ffCommand("F1F1A002-7C3B-4E2A-9A1D-5B0E46F1F1F1");
BLECharacteristic ffRoster ("F1F1A003-7C3B-4E2A-9A1D-5B0E46F1F1F1");

SX1262 radio = new Module(PIN_LORA_NSS, PIN_LORA_DIO1, PIN_LORA_RST, PIN_LORA_BUSY);
Adafruit_NeoPixel leds(NUM_LEDS, PIN_LEDS, NEO_GRB + NEO_KHZ800);

// ---------- State ----------
uint8_t  myId;                  // derived from the chip id
uint32_t groupKey = 0;          // 0 = not in a group
uint16_t seq = 0;
volatile bool loraFlag = false;
bool     finding = false;  uint32_t findingUntil = 0;
int8_t   bestRssi = -127;  uint32_t bestRssiAt = 0;
uint32_t sosUntil = 0;
struct Seen { uint8_t id; int8_t rssi; uint8_t batt; uint32_t at; } seen[12];
struct Recent { uint8_t from; uint16_t seq; } recent[16]; uint8_t recentIdx = 0;

// ---------- Helpers ----------
uint8_t batteryPercent() {
  // XIAO nRF52840: VBAT divider on P0.31, enabled by pulling P0.14 low.
  pinMode(14, OUTPUT); digitalWrite(14, LOW);
  analogReference(AR_INTERNAL_3_0); analogReadResolution(12);
  float v = analogRead(PIN_VBAT) * 3.0f / 4096.0f * 2.961f;
  digitalWrite(14, HIGH);
  int pct = (int)((v - 3.3f) / (4.2f - 3.3f) * 100.0f);
  return (uint8_t)constrain(pct, 0, 100);
}

uint32_t macOf(const Packet& p) {        // FNV-1a over the packet body, keyed with the group key.
  uint32_t h = 2166136261u ^ groupKey;   // Stand-in for a real truncated HMAC-SHA256 (nRF52 has a crypto block for that).
  const uint8_t* b = (const uint8_t*)&p;
  for (int i = 0; i < 8; i++) { h ^= b[i]; h *= 16777619u; }
  return h;
}

void buzz(uint16_t ms) { digitalWrite(PIN_MOTOR, HIGH); delay(ms); digitalWrite(PIN_MOTOR, LOW); }
void pattern(const uint16_t* p, int n) { for (int i = 0; i < n; i++) { if (i % 2 == 0) buzz(p[i]); else delay(p[i]); } }

void showLeds(int n, uint32_t color) {
  for (int i = 0; i < NUM_LEDS; i++) leds.setPixelColor(i, i < n ? color : 0);
  leds.show();
}
const uint32_t AMBER = 0xF5A020, RED = 0xFF1830, GREEN = 0x30FF60;

void send(MsgType type, uint8_t target = 0xFF) {
  if (!groupKey && type != JOIN) return;
  Packet p = { 0xF1, type, myId, 0, ++seq, batteryPercent(), 0, 0 };
  if (type == PING) p.rssi = (int8_t)target;   // for PING the rssi byte carries the target id
  p.mac = macOf(p);
  digitalWrite(PIN_RF_SW, HIGH);
  radio.transmit((uint8_t*)&p, sizeof(p));
  radio.startReceive();
}

void forwardToApp(const Packet& p) {
  if (Bluefruit.connected()) ffEvents.notify((const uint8_t*)&p, sizeof(p));
}

bool seenBefore(const Packet& p) {
  for (auto& r : recent) if (r.from == p.from && r.seq == p.seq) return true;
  recent[recentIdx++ % 16] = { p.from, p.seq };
  return false;
}

// ---------- Incoming LoRa ----------
void onLora() { loraFlag = true; }

void handlePacket(Packet& p, float rssi) {
  if (p.magic != 0xF1 || p.from == myId) return;
  if (p.type == JOIN) { if (!groupKey) { groupKey = p.mac; pattern((const uint16_t[]){80, 80, 80}, 3); } return; }
  if (p.mac != macOf(p) || seenBefore(p)) return;
  p.rssi = (int8_t)constrain((int)rssi, -127, 0);
  forwardToApp(p);
  switch (p.type) {
    case COME_FIND: pattern((const uint16_t[]){120, 100, 120}, 3); showLeds(4, AMBER); break;
    case HELP:      pattern((const uint16_t[]){250, 120, 250}, 3); break;
    case SOS:       sosUntil = millis() + 30000; break;
    case CANCEL:    sosUntil = 0; buzz(60); showLeds(0, 0); break;
    case PING:      if ((uint8_t)p.rssi == myId || (uint8_t)p.rssi == 0xFF) { pattern((const uint16_t[]){100, 80, 100, 80, 100}, 5); showLeds(4, AMBER); } break;
    case ASK_CHECKIN: buzz(60); break;
    default: break;
  }
  // Simple one-hop relay so bands at the edge of range still hear each other.
  if (p.hops == 0) { p.hops = 1; delay(random(20, 120)); digitalWrite(PIN_RF_SW, HIGH); radio.transmit((uint8_t*)&p, sizeof(p)); radio.startReceive(); }
}

// ---------- BLE: app commands and band-to-band proximity ----------
void onCommand(uint16_t, BLECharacteristic*, uint8_t* data, uint16_t len) {
  if (len < 1) return;
  uint8_t target = len > 1 ? data[1] : 0xFF;
  send((MsgType)data[0], target);
  if (data[0] == LEAVE) groupKey = 0;
}

void onScan(ble_gap_evt_adv_report_t* report) {
  // Other bands advertise manufacturer data: [0xF1, groupHash, id, battery]
  uint8_t buf[8];
  uint8_t n = Bluefruit.Scanner.parseReportByType(report, BLE_GAP_AD_TYPE_MANUFACTURER_SPECIFIC_DATA, buf, sizeof(buf));
  if (n >= 6 && buf[2] == 0xF1 && buf[3] == (uint8_t)(groupKey & 0xFF)) {
    uint8_t id = buf[4];
    for (auto& s : seen) if (s.id == id || s.at == 0 || millis() - s.at > 10000) { s = { id, report->rssi, buf[5], millis() }; break; }
    if (report->rssi > bestRssi || millis() - bestRssiAt > 1500) { bestRssi = report->rssi; bestRssiAt = millis(); }
  }
  Bluefruit.Scanner.resume();
}

void startAdvertising() {
  uint8_t mfg[6] = { 0xFF, 0xFF, 0xF1, (uint8_t)(groupKey & 0xFF), myId, batteryPercent() }; // 0xFFFF = test company id
  Bluefruit.Advertising.clearData();
  Bluefruit.Advertising.addFlags(BLE_GAP_ADV_FLAGS_LE_ONLY_GENERAL_DISC_MODE);
  Bluefruit.Advertising.addService(ffService);
  Bluefruit.Advertising.addManufacturerData(mfg, sizeof(mfg));
  Bluefruit.ScanResponse.addName();
  Bluefruit.Advertising.restartOnDisconnect(true);
  Bluefruit.Advertising.setInterval(1600, 1600);     // 1 s (units of 0.625 ms)
  Bluefruit.Advertising.start(0);
}

void publishRoster() {
  if (!Bluefruit.connected()) return;
  uint8_t buf[1 + 3 * 12]; uint8_t n = 0; buf[n++] = batteryPercent();
  for (auto& s : seen) if (s.at && millis() - s.at < 10000) { buf[n++] = s.id; buf[n++] = (uint8_t)s.rssi; buf[n++] = s.batt; }
  ffRoster.notify(buf, n);
}

// ---------- Buttons: single / double / long ----------
int readButtons() { int v = analogRead(PIN_BUTTONS); return v > 3600 ? 0 : v > 2200 ? 2 : v > 950 ? 1 : 3; }

enum Gesture { NONE, B1_SINGLE, B1_DOUBLE, B1_LONG, B2_SINGLE, B2_DOUBLE, B2_LONG, BOTH_LONG };
Gesture pollGesture() {
  static int last = 0, clicks = 0, lastBtn = 0; static uint32_t downAt = 0, upAt = 0; static bool longFired = false;
  int b = readButtons(); uint32_t now = millis();
  if (b && !last) { downAt = now; longFired = false; lastBtn = b; }
  if (b && !longFired) {
    if (b == 3 && now - downAt > 5000) { longFired = true; clicks = 0; last = b; return BOTH_LONG; }
    if (b == 1 && now - downAt > 900)  { longFired = true; clicks = 0; last = b; return B1_LONG; }
    if (b == 2 && now - downAt > 3000) { longFired = true; clicks = 0; last = b; return B2_LONG; }
  }
  if (!b && last && !longFired) { clicks++; upAt = now; }
  last = b;
  if (!b && clicks && now - upAt > 320) {
    Gesture g = lastBtn == 1 ? (clicks >= 2 ? B1_DOUBLE : B1_SINGLE) : (clicks >= 2 ? B2_DOUBLE : B2_SINGLE);
    clicks = 0; return g;
  }
  return NONE;
}

// ---------- Setup / loop ----------
void setup() {
  pinMode(PIN_MOTOR, OUTPUT); digitalWrite(PIN_MOTOR, LOW);
  pinMode(PIN_RF_SW, OUTPUT); digitalWrite(PIN_RF_SW, HIGH);
  analogReadResolution(12);
  leds.begin(); leds.setBrightness(100); showLeds(0, 0);
  myId = (uint8_t)(NRF_FICR->DEVICEID[0] & 0xFE) | 1;

  int st = radio.begin(LORA_FREQ, LORA_BW, LORA_SF, LORA_CR, LORA_SYNC, LORA_DBM, 8, TCXO_V);
  if (st != RADIOLIB_ERR_NONE) { showLeds(1, RED); }
  radio.setDio2AsRfSwitch(true);
  radio.setDio1Action(onLora);
  radio.startReceive();

  Bluefruit.begin(1, 1);                 // 1 peripheral link (the app), 1 central (scanning other bands)
  Bluefruit.setTxPower(0);
  Bluefruit.setName("Firefly");
  ffService.begin();
  ffEvents.setProperties(CHR_PROPS_NOTIFY);  ffEvents.setPermission(SECMODE_OPEN, SECMODE_NO_ACCESS); ffEvents.setFixedLen(12); ffEvents.begin();
  ffCommand.setProperties(CHR_PROPS_WRITE);  ffCommand.setPermission(SECMODE_NO_ACCESS, SECMODE_OPEN); ffCommand.setMaxLen(4); ffCommand.setWriteCallback(onCommand); ffCommand.begin();
  ffRoster.setProperties(CHR_PROPS_NOTIFY);  ffRoster.setPermission(SECMODE_OPEN, SECMODE_NO_ACCESS); ffRoster.setMaxLen(40); ffRoster.begin();
  startAdvertising();
  Bluefruit.Scanner.setRxCallback(onScan);
  Bluefruit.Scanner.setInterval(160, 80);   // 100 ms window every 100 ms when finding; idle duty is reduced in loop
  Bluefruit.Scanner.start(0);

  buzz(80);   // hello
}

void loop() {
  uint32_t now = millis();

  if (loraFlag) {
    loraFlag = false; Packet p;
    if (radio.readData((uint8_t*)&p, sizeof(p)) == RADIOLIB_ERR_NONE) handlePacket(p, radio.getRSSI());
    radio.startReceive();
  }

  switch (pollGesture()) {
    case B1_SINGLE: finding = true; findingUntil = now + 60000; break;
    case B1_DOUBLE: send(COME_FIND); pattern((const uint16_t[]){80, 60, 80}, 3); break;
    case B1_LONG:
      if (!groupKey) { groupKey = (uint32_t)random(1, 0x7FFFFFFF); send(JOIN); pattern((const uint16_t[]){80, 80, 80}, 3); } // pairing: first band starts the group
      else { send(CHECKIN); buzz(80); showLeds(2, GREEN); delay(300); showLeds(0, 0); }
      startAdvertising();
      break;
    case B2_SINGLE: send(HELP); buzz(150); break;               // discreet: no light
    case B2_DOUBLE: send(CANCEL); sosUntil = 0; buzz(60); showLeds(0, 0); break;
    case B2_LONG:   send(SOS); sosUntil = now + 30000; break;
    case BOTH_LONG: send(LEAVE); groupKey = 0; pattern((const uint16_t[]){300, 100, 300}, 3); startAdvertising(); break;
    default: break;
  }

  // Finding mode: strongest group RSSI → LED count and pulse period (2.5 s far … 0.25 s right here)
  static uint32_t nextPulse = 0;
  if (finding) {
    if (now > findingUntil) { finding = false; showLeds(0, 0); }
    else {
      int r = (now - bestRssiAt < 3000) ? bestRssi : -127;
      int n = r > -55 ? 4 : r > -68 ? 3 : r > -80 ? 2 : r > -100 ? 1 : 0;
      showLeds(n, AMBER);
      uint16_t period = n == 4 ? 250 : n == 3 ? 500 : n == 2 ? 1000 : 2500;
      if (now >= nextPulse) { buzz(n >= 2 ? 90 : 60); nextPulse = now + period; }
    }
  }

  // SOS: flash red and buzz until cancelled or 30 s
  if (sosUntil && now < sosUntil) { bool on = (now / 250) % 2; showLeds(on ? 4 : 0, RED); if (on && (now % 1000) < 20) buzz(200); }
  else if (sosUntil) { sosUntil = 0; showLeds(0, 0); }

  static uint32_t nextRoster = 0;
  if (now > nextRoster) { publishRoster(); nextRoster = now + 2000; }

  // Let the SoftDevice sleep the CPU until the next event (BLE, LoRa interrupt, or the 10 ms tick)
  delay(10);
}
