# Watch direction: technical feasibility check (2026-10-27)

**Verdict: it can be built with parts that exist today, with three fixes: weight, battery margin and light through the dial.** Nothing here has been approved yet; the concept page, website, video, app, firmware and BOM still describe the bangle.

The design under review is at [`docs/watch/`](../../docs/watch/index.html): a 34 mm dress watch with the crown as the Find button, a pusher at 2 o'clock as Safety, a mother-of-pearl dial lit through its hour markers, antennas in the strap, and long-range tracking.

## Requirement: at least 6 miles of location tracking, even with a weak signal

A direct watch-to-watch radio can't do 6 miles in a city. Wrist to wrist, LoRa reaches about 50-150 m in a packed club and 300 m-1 km outdoors. Six miles has to come from networks:

| Layer | Reach | Weak or no signal | Hardware and cost |
|---|---|---|---|
| Watch to watch (LoRa, SX1262) | 50 m-1 km, more with relays | Works with zero bars | Already in the design |
| **Cellular LTE-M / NB-IoT (core)** | 6 miles and beyond, anywhere with IoT coverage | NB-IoT allows about 164 dB maximum coupling loss and LTE-M about 161 dB, roughly 20 dB more than normal phone LTE | Nordic nRF9151 (LTE-M + NB-IoT + GPS, 12.1 × 11.1 × 1.2 mm). Data: 1NCE, 500 MB over 10 years for $10 + $1 SIM |
| Amazon Sidewalk (free fallback) | Hundreds of metres to about half a mile per Echo/Ring bridge; Amazon claims about 90% of the US population | Same LoRa radio; devices roam between bridges | No new parts: Nordic supports Sidewalk on nRF52840 + SX1262. A LoRa message is limited to 19 bytes, so the position must be compressed |
| Apple Find My / Google Find Hub (indoor fallback) | Wherever a phone passes | Needs no signal at the watch | No new parts (nRF52840 supports Find My; needs an Apple MFi license). One network at a time per device |

This matches the recommendation in [`build-plan/phase1-addendum-2026-10-27.md`](../../build-plan/phase1-addendum-2026-10-27.md): LTE-M is the option that reliably reaches someone in another borough.

## Checks

| Item | Verdict | Notes |
|---|---|---|
| 6-mile tracking | Feasible | Via cellular where LTE-M/NB-IoT coverage exists; Sidewalk and phone crowds as fallbacks. Test coverage where the group actually goes out. |
| Battery | Feasible, tight | See the budget below. Use a 200-210 mAh round cell and cap GPS searching indoors. |
| Weight | 1-2 g over | About 31 g as drawn. A 32 mm case and a 2.2 mm strap bring it to about 28-29 g. Steel or brass cases can't get under 30 g. |
| Thickness | Feasible | About 12 mm production stack (caseback 0.8, motor 2.0, battery 3.0, board 0.8, tallest parts 2.0, dial and hands 1.5, crystal 1.2). The dev-board prototype is about 15 mm. |
| Chip-driven hands | Proven | Hybrid smartwatches ship this (Frederique Constant Hybrid, MyKronoz ZeTime). |
| Antennas in strap | Proven idea, needs engineering | Patented approach (for example US10027023). A 915 MHz quarter-wave antenna is about 8 cm and fits one strap half. It needs a reliable contact through the lug and tuning on a real wrist. |
| Light through the dial | Needs a prototype | Mother-of-pearl passes light only when very thin and fragile. Plan: a small translucent window under each marker. |
| Pointing toward a friend | Outdoors only | Needs both GPS fixes plus a compass calibrated inside the metal case. Indoors it falls back to hot or cold by signal strength. |
| Certification | Plan for months | FCC Part 15, carrier approval for cellular (the pre-certified nRF9151 helps), Amazon Sidewalk qualification, Apple MFi or Google's program. |

## Battery budget (185 mAh round cell, 85% usable)

Starting from the Phase 1 budget (typical 3.54 mA, heavy 12.71 mA, worst 20.58 mA), the watch adds:

- Sidewalk uplinks: about 150 ms at about 100 mA per message, plus receive windows
- Find My advertising: about 0.05 mA
- The hand stepper: about 0.02 mA

| Night | Average | Runtime |
|---|---|---|
| Typical | 3.8 mA | about 41 h |
| Heavy | 13.1 mA | about 12.0 h |
| Worst (GPS searching all night) | 21.0 mA | about 7.5 h, which needs the firmware GPS cap |
| Heavy + cellular every 2 min | 13.8 mA | about 11.4 h |
| Heavy + cellular every 5 min | 13.4 mA | about 11.7 h |

Each cellular report is assumed to cost about 2 s at 45 mA, based on a forum measurement on the nRF9160. Measure it on real hardware. A 210 mAh cell puts the heavy night with cellular back to about 13 h. Off-the-shelf round cells exist, for example the Grepow 3030028 (185 mAh, about 30 × 2.9 mm) and the 3030027 (170 mAh).

## Weight budget (g)

| Part | g |
|---|---|
| Titanium case + lugs, 34 mm, gold PVD | 12.0 |
| Crystal (1.0 mm sapphire) | 2.5 |
| Mother-of-pearl dial, 0.4 mm | 0.7 |
| Round LiPo, 185 mAh | 3.6 |
| Board with nRF52840, SX1262, nRF9151 and passives | 2.0 |
| GPS/cellular antennas and strap contacts | 1.5 |
| Hand stepper + hands | 1.0 |
| Vibration motor | 0.8 |
| Crown, pusher, gaskets | 0.6 |
| Leather strap, 16 mm, 2.5 mm average | 5.5 |
| Titanium buckle | 1.2 |
| **Total** | **about 31** |

To reach 28-29 g: use a 32 mm case (-1.5 g), a 2.2 mm strap (-1 g) and a 0.8 mm crystal (-0.5 g). These are estimates; weigh the real parts.

## Sources

- Nordic, Sidewalk hardware setup (nRF52840 with SX1262 shield): https://nrfconnectdocs.nordicsemi.com/addons/addon-sidewalk/latest/setting_up_sidewalk_environment/setting_up_hardware.html
- AWS, track-and-trace on Sidewalk (19-byte LoRa payload, roaming, location via GNSS/Wi-Fi): https://aws.amazon.com/blogs/iot/building-track-and-trace-applications-using-aws-iot-core-for-amazon-sidewalk/
- GeekWire, Sidewalk covers about 90% of the US population: https://www.geekwire.com/2023/amazon-says-sidewalk-reaches-90-of-u-s-population-as-it-opens-network-to-developers/
- 5G Technology World, Sidewalk range about half a mile: https://www.5gtechnologyworld.com/how-amazon-sidewalk-differs-from-wi-fi-cellular-and-lorawan-networks/
- Semtech, Sidewalk LoRa versus FSK range test: https://blog.semtech.com/taking-your-application-beyond-the-sidewalk-the-longest-range-mode-of-amazons-new-protocol
- Nordic, nRF9151 announcement: https://www.nordicsemi.com/Nordic-news/2024/09/nRF9151-the-smallest-and-lowest-power-cellular-IoT-solution-for-the-massive-IoT-market
- Nordic, nRF9151 package dimensions: https://docs.nordicsemi.com/r/bundle/ps_nrf9151/page/mec_spec.html
- IoT For All, NB-IoT versus LTE-M coupling loss: https://iotforall.com/nb-iot-vs-lte-m-a-comparison
- 1NCE, $10 for 10 years: https://1nce.com/en-us/1nce-connect/10-dollars-for-10-years
- Nordic, Apple Find My network support: https://www.nordicsemi.com/Products/Technologies/Apple-Find-My-network
- Find Hub (Wikipedia): https://en.wikipedia.org/wiki/Find_Hub
- One network at a time for dual-network trackers: https://www.inkl.com/news/new-chipolo-pop-bluetooth-trackers-work-with-google-and-apple-find-my-device-networks-but-there-s-a-catch
- Grepow round LiPo 185 mAh: https://grepow.com/battery-news/grepow-185mah-3-8v-round-shaped-lipo-battery-3030028.html
- Grepow round LiPo 170 mAh: https://grepow.com/battery-news/grepow-170mah-3-7v-round-shaped-lipo-battery-3030027.html
- Nordic DevZone, nRF9160 LTE-M current profile: https://devzone.nordicsemi.com/f/nordic-q-a/120415/nrf9160-lte-m-current-profile
- Hybrid analog watch patent: https://patents.google.com/patent/US10481559
- Antenna embedded in a watch band patent: https://patents.google.com/patent/US10027023
