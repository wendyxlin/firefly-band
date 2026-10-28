# Firefly v2 bracelet: technical design and feasibility (2026-10-28)

**Verdict: buildable with parts that exist today, but battery space is the main constraint.** The design follows the team's v2 design board: a slim gold bangle with a soft capsule on top that carries two round buttons and one pinhole light, in gold, silver, rose gold and black. To keep 6-mile range and get through a heavy night, the battery is split. One cell sits in the capsule and a second sits in a slim clasp under the wrist.

This is the **v2 proposal**. The v1 bangle (`hardware/`, `docs/`) and the watch directions (`design/watch/`, `afterglow-watch/`) are kept as they are.

## Button map (firmware)

| Input | Gesture | Action | Feedback | Cancel |
|---|---|---|---|---|
| Button 1 (engraved dot) | Press | **Find friends**: UWB ranging to the group at 10 Hz for 60 s | Buzz pulses and the light pulses pink faster as the distance drops | Press again |
| Button 1 | Press twice | **Come find me**: message to the group (BLE → phone if paired, else LoRa, else cellular) | Two short buzzes; the light blinks amber | Press twice again |
| Button 2 (engraved line) | Press | **I'm home** to the group | Two short buzzes; the light glows green when delivered | Press twice within 5 s; one long buzz confirms |
| Both buttons | Hold 3 s | **SOS**: after a 5–10 s grace window (set in the app), position to the group and the backup contact, repeated every 30 s until acknowledged | Three rising buzzes during the hold; the light blinks red | Press either button twice during the grace window |
| None | Automatic | **Separation alert**: outside the radius (10/20/30 m) for longer than the delay (1/2/5 min) | Long buzz; the light breathes pink | Walk back, or dismiss in the app |

Each switch needs 260 gf, so a single button won't fire in a bag. Holding both for 3 s makes an accidental SOS very unlikely.

## Hardware layout

| Part | Where | Notes |
|---|---|---|
| Capsule | Top of the wrist, 40 × 13.6 × 6.8 mm | Metal frame (titanium or brass, PVD colour) with a ceramic underside, which acts as the radio window |
| Board | Inside the capsule, stadium 30 × 10.4 mm, 0.8 mm | nRF52840 (BLE, control), SX1262 (LoRa), nRF9151 (LTE-M/NB-IoT + GNSS, 12.1 × 11.1 × 1.2 mm), DW3110 (UWB, 3.1 × 3.5 mm), RGB LED |
| Buttons | On the capsule, 9 mm caps | Tactile switches under domed caps with an engraved dot and line |
| Light | Between the buttons | One RGB LED under a 1.3 mm sapphire window |
| Battery | Capsule cell 85 mAh (about 27 × 10.4 × 3.0 mm) + clasp cell 60 mAh (26 × 6.4 × 3.0 mm) | About 145 mAh together. Wires run through the hollow band. |
| Motor | Under the capsule | 8 mm coin ERM against the skin |
| Antennas | The band | The metal band, split by an insulating gap at the hinge, acts as the LoRa (915 MHz) and LTE antenna. A UWB chip antenna sits under the ceramic underside, angled out sideways. |
| Charging | Under the capsule | Two magnetic pogo pins |

## Range: at least 6 miles, even with weak signal

| Layer | Reach | Weak or no signal | Part |
|---|---|---|---|
| UWB | 0–30 m. About ±10–30 cm with line of sight; reliable to about 10–20 m on wrists in a crowd | Bracelet to bracelet, no network | Qorvo DW3110 (TX 14–17 mA, RX 16–19 mA, 850 nA sleep) |
| LoRa | 30 m–1 km (50–150 m in a packed club) | Zero bars | Semtech SX1262 |
| Cellular LTE-M / NB-IoT | 1 km to 6 miles and beyond, wherever there's IoT coverage | NB-IoT allows about 164 dB maximum coupling loss and LTE-M about 161 dB, about 20 dB better than phone LTE | Nordic nRF9151. Data: 1NCE, 500 MB over 10 years for $10 + $1 SIM |
| Amazon Sidewalk | About half a mile per Echo/Ring bridge; about 90% of the US population | Same LoRa radio; 19-byte payload | No new parts |
| Apple Find My / Google Find Hub | Anywhere a phone passes | Needs no signal at the bracelet | Needs Apple MFi or Google's program; one network at a time |

## Checks

| Item | Verdict | Notes |
|---|---|---|
| Two buttons + hidden SOS | Feasible | Firmware only: single, double and long-press detection per button, plus a both-buttons hold. |
| Fit in the capsule | Feasible, tight | Stack from the skin up: ceramic 0.6 mm, battery 3.0, board 0.8, tallest parts 1.2, top wall 0.8, plus the button travel, for 6.4–6.8 mm total. The prototype is bigger (see below). |
| Battery | **Tight** | The capsule cell alone gives only about 5 h on a heavy night. With the clasp cell it's about 9 h (budget below). |
| Band as antenna | Needs RF engineering | A metal loop around a wrist detunes easily. It needs a feed across the hinge gap and tuning on real wrists. Fallback: a flex antenna inside the hollow band with a resin inlay strip. |
| UWB through the ceramic underside | Needs a prototype | Metal blocks UWB and the wrist absorbs it, so the antenna has to radiate out of the capsule's ceramic sides. Expect the best range when wrists face each other. |
| Separation vs signal loss | Firmware rule | A dropout longer than the alert delay counts as a separation, and the app says "connection lost" rather than "left the radius". |
| Weight | Feasible | About 15 g in titanium; about 22 g in gold-plated brass. |
| Waterproofing | Splash-proof | Button seals and pogo pins. No swimming. |
| Certification | Plan for months | FCC Part 15 (including Subpart F for UWB), carrier approval for cellular, Sidewalk qualification, Apple MFi or Google's program. |

## Battery budget (85 mAh + 60 mAh = 145 mAh, 85% usable)

The averages are the same as the v2 watch model: the v1 Phase 1 figures plus UWB background ranging (0.18 mA) and 20 minutes of finding on a heavy night (0.05 mA).

| Night | Average | Runtime (145 mAh) | Capsule cell only (85 mAh) |
|---|---|---|---|
| Typical | 4.0 mA | about 31 h | about 18 h |
| Heavy | 13.3 mA | about 9.2 h | about 5.4 h |
| Worst (GPS searching all night) | 21.2 mA | about 5.8 h, needs the firmware GPS cap | about 3.4 h |
| Heavy + cellular every 2 min | 14.0 mA | about 8.8 h | about 5.1 h |
| Heavy + cellular every 5 min | 13.6 mA | about 9.0 h | about 5.3 h |

An hour of SOS, with a cellular report every 30 s, costs about 3 mAh. To get more time without a bigger capsule:
- Send cellular reports only for events (I'm home, come find me, SOS) and every 10 minutes otherwise.
- Cap GPS searching indoors.

## Weight budget (g, titanium)

| Part | g |
|---|---|
| Band, 3.2 × 2.2 mm, about 132 mm long, hollow titanium | 2.6 |
| Capsule frame + button caps | 2.8 |
| Ceramic underside + sapphire light window | 0.8 |
| Clasp + hinge | 1.2 |
| Board with radios and passives | 2.3 |
| Batteries (85 + 60 mAh) | 3.4 |
| Motor | 0.8 |
| Antenna feed, seals, pogo pins | 0.6 |
| **Total** | **about 14.5** |

## Prototype plan

The prototype uses dev boards, so it is bigger than the drawn design. It uses a printed capsule about 48 × 30 × 18 mm on a wide band. It proves the button gestures, UWB finding and the separation alert, LoRa and cellular. It doesn't prove the finished size. Parts are in [`BOM.csv`](BOM.csv): about $247 and 38 g per prototype, so you need two to test finding.

**Pin check:** the XIAO + Wio-SX1262 stack has only 3 free pins (D0, D6, D7) plus 2 NFC pads. The UWB module and the cellular board each need a UART. Two fixes, both off the shelf:
- Use a RAK4631 WisBlock core instead: the same nRF52840 + SX1262, with two UARTs and more GPIO.
- Let the DWM3001C's own nRF52833 drive the LED and motor.

Tests:
- UWB distance at 1, 5, 10, 20 and 30 m in a bar and in a hallway
- the both-buttons SOS gesture in a bag, to make sure it doesn't fire by accident
- I'm home over cellular from a basement
- a 6-mile report across boroughs

## Sources

- Qorvo DW3110 package, current and channels (everything RF): https://www.everythingrf.com/products/rf-transceivers/qorvo/531-483-dw3110
- Qorvo DWM3001C module (DW3110 + nRF52833, 27 × 19.13 × 3.2 mm, from $59.37): https://rfmw.com/products/detail/dwm3001c-qorvo/692453/
- Circuit Dojo nRF9151 Feather: https://github.com/circuitdojo/nrf9151-feather
- nRF9160 Feather launch price ($99, for reference): https://www.electronics-lab.com/news/nrf9160-feather-launches-for-99-with-gps-support/
- Nordic nRF9151: https://www.nordicsemi.com/Nordic-news/2024/09/nRF9151-the-smallest-and-lowest-power-cellular-IoT-solution-for-the-massive-IoT-market
- Nordic nRF9151 package dimensions: https://docs.nordicsemi.com/r/bundle/ps_nrf9151/page/mec_spec.html
- NB-IoT versus LTE-M coupling loss: https://iotforall.com/nb-iot-vs-lte-m-a-comparison
- 1NCE, $10 for 10 years: https://1nce.com/en-us/1nce-connect/10-dollars-for-10-years
- Nordic, Sidewalk on nRF52840 + SX1262: https://nrfconnectdocs.nordicsemi.com/addons/addon-sidewalk/latest/setting_up_sidewalk_environment/setting_up_hardware.html
- AWS, Sidewalk track and trace (19-byte payload, roaming): https://aws.amazon.com/blogs/iot/building-track-and-trace-applications-using-aws-iot-core-for-amazon-sidewalk/
- GeekWire, Sidewalk covers about 90% of the US population: https://www.geekwire.com/2023/amazon-says-sidewalk-reaches-90-of-u-s-population-as-it-opens-network-to-developers/
- Nordic, Apple Find My support: https://www.nordicsemi.com/Products/Technologies/Apple-Find-My-network
- Nordic DevZone, nRF9160 LTE-M current profile: https://devzone.nordicsemi.com/f/nordic-q-a/120415/nrf9160-lte-m-current-profile
- Antenna embedded in a band (patent): https://patents.google.com/patent/US10027023
