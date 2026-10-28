# Afterglow v2: technical design and feasibility (2026-10-27)

**Verdict: buildable with parts that exist today.** The v2 changes (two buttons remapped to I'm Home and SOS, plus ultra-wideband for the buddy radius) add about 0.9 g and about 0.2 mA. A 210 mAh cell covers that. The open risks are the same as the v1 watch: weight is 2–3 g over the 29 g target as drawn, the dial needs light windows, and certification takes months. One new risk: the glowing marker can point toward your circle only outdoors (see below).

This is a **v2 proposal**. The v1 bangle and the v1 watch direction are unchanged, in `hardware/`, `design/watch/` and `docs/`.

## What changed from the v1 watch

| | v1 watch (in review) | v2 Afterglow |
|---|---|---|
| Name | Firefly | Afterglow, "Stay close. Go out." (from the team's Drive demo, `afterglow_demo.html`) |
| Crown, 3 o'clock | Find | **I'm Home**: press to send; press again within 5 s to cancel; dial sweeps green when delivered |
| Pusher, 2 o'clock (red ring) | Safety | **SOS**: hold 3 s; press twice during the 5–10 s grace window to cancel; dial pulses red |
| Finding a friend | Watch button | **App**: Friends tab, distance from UWB, no map or arrow up close |
| Come Find Me | — | **App**: one tap shares your position with the circle |
| Separation | — | **Automatic**: buddy radius 10–30 m, alert delay 1/2/5 min; watch buzzes, marker toward the circle glows lavender |
| Up-close distance | Bluetooth signal strength (hot or cold) | **UWB ranging**, about ±10 cm |
| Palette | Gold and amber | Lavender on deep plum, lavender glow |

## Two-button map (firmware)

| Button | Gesture | Action | Feedback | Cancel |
|---|---|---|---|---|
| Crown | Single press | Send I'm Home to the circle (BLE → phone if paired, else LoRa/cellular direct) | Two short buzzes confirm it's sent; green sweep around the dial when it's delivered to the circle | Second press within 5 s; one long buzz confirms the cancel |
| Pusher | Hold 3 s | Start SOS: grace window 5–10 s (set in app), then send position to the circle and the backup contact; repeat every 30 s until a friend acknowledges or you cancel | Three rising buzzes during the hold; dial pulses red during grace and after sending | Two presses during grace; after sending, hold 3 s again and confirm in the app |
| Both | Hold 10 s | Restart the watch | Long buzz | — |

Both switches are 260 gf, so they don't fire in a bag. The crown also turns for setting the time; turning is ignored by the alert logic.

## Range: at least 6 miles, even with weak signal

| Layer | Reach | Weak or no signal | Part |
|---|---|---|---|
| UWB (new in v2) | 0–30 m, ±10 cm | Watch to watch, no network | Qorvo DW3110, 3.1 × 3.5 mm WLCSP, TX 14–17 mA, RX 16–19 mA, 850 nA sleep, channels 5 and 9 |
| LoRa | 30 m–1 km (50–150 m in a packed club) | Zero bars | Semtech SX1262 |
| Cellular LTE-M / NB-IoT (core long-range link) | 1 km to 6 miles and beyond, wherever there is IoT coverage | NB-IoT allows about 164 dB maximum coupling loss and LTE-M about 161 dB, about 20 dB better than phone LTE: it gets into basements | Nordic nRF9151 (LTE-M + NB-IoT + GNSS, 12.1 × 11.1 × 1.2 mm). Data: 1NCE, 500 MB over 10 years for $10 + $1 SIM |
| Amazon Sidewalk | About half a mile per Echo/Ring bridge, about 90% of the US population covered | Uses the same LoRa radio; 19-byte payload limit | No new parts (Nordic supports Sidewalk on nRF52840 + SX1262) |
| Apple Find My / Google Find Hub | Anywhere a phone passes | Needs no signal at the watch | No new parts; needs Apple MFi or Google's program; one network at a time |

The watch tries the layers in that order and never needs the wearer's phone to send I'm Home or SOS.

## Checks

| Item | Verdict | Notes |
|---|---|---|
| Two buttons | Feasible | Same switches and case as the v1 watch, only the firmware mapping changes. |
| Buddy radius with UWB | Feasible at 10–20 m; 30 m is at the edge | Distance between watches every 2 s for up to 4 friends, accurate to about 10–30 cm in line of sight. On wrists in a packed club, bodies block the 6.5–8 GHz signal, so expect reliable readings to roughly 10–20 m and dropouts beyond. A dropout longer than the alert delay (1/2/5 min) counts as a separation, and the app words it as "connection lost" rather than "left the radius". This matches the 2026-10-28 build-plan addendum. |
| Separation vs signal loss | Feasible, firmware rule | If UWB drops, the watch falls back to LoRa distance and the app shows "signal lost", not "left the radius". This follows the demo. |
| Marker pointing toward the circle | **Outdoors only** | A single UWB antenna measures distance, not direction. Outdoors, the watch uses both GPS fixes and its compass. Indoors, it lights all markers in a slow lavender pulse instead. True indoor direction needs a 2-antenna PDoA chip (Qorvo DW3220), about +0.3 g and a bigger board; worth a later spin. |
| Friend-finding in the app | Feasible | The phone shows the watch-to-watch UWB distance relayed over BLE. iPhones and Pixels with UWB could range directly, but that needs Apple's and Google's accessory programs. |
| 6-mile tracking | Feasible | Cellular where LTE-M/NB-IoT coverage exists; Sidewalk and phone crowds as fallbacks. Test coverage in the venues the group uses. |
| UWB antenna placement | Needs a prototype | A UWB antenna can't sit under metal. Put a small chip antenna behind the mother-of-pearl dial at 12 o'clock, with a cutout in the movement plate. UWB at 6.5–8 GHz is absorbed by the wrist, so expect the best range when watches face each other. |
| Battery | Feasible | 210 mAh round cell; see the budget below. |
| Weight | 2–3 g over target | About 32 g as drawn; about 29 g with a 32 mm case, 2.2 mm strap and 0.8 mm crystal. |
| Thickness | Feasible | About 12 mm production stack; UWB fits beside the nRF9151 on the same board. Dev-board prototype about 16 mm. |
| Light through the dial | Needs a prototype | Translucent windows under each marker, lit lavender (separation), green (I'm Home) or red (SOS). |
| Certification | Plan for months | FCC Part 15 (including Subpart F for UWB), carrier approval for cellular, Sidewalk qualification, Apple MFi or Google's program. |

## Battery budget (210 mAh round cell, 85% usable)

v1 watch figures plus UWB: background ranging to 4 friends every 2 s (about 5 ms at 18 mA per exchange, 0.18 mA average) and 20 minutes of 10 Hz finding on a heavy night (0.05 mA average).

| Night | Average | Runtime (210 mAh) | Runtime (185 mAh, for comparison) |
|---|---|---|---|
| Typical | 4.0 mA | about 45 h | about 39 h |
| Heavy | 13.3 mA | about 13.4 h | about 11.8 h |
| Worst (GPS searching all night) | 21.2 mA | about 8.4 h, needs the firmware GPS cap | about 7.4 h |
| Heavy + cellular every 2 min | 14.0 mA | about 12.7 h | about 11.2 h |
| Heavy + cellular every 5 min | 13.6 mA | about 13.1 h | about 11.5 h |

An hour of SOS, with a cellular report every 30 s, costs about 3 mAh (120 reports × 2 s × 45 mA). I'm Home costs one report. These are models, so measure on hardware, especially the UWB receive windows, which depend on how tightly the watches synchronise over BLE.

## Weight budget (g)

| Part | g |
|---|---|
| Titanium case + lugs, 34 mm, gold PVD | 12.0 |
| Crystal (1.0 mm sapphire) | 2.5 |
| Mother-of-pearl dial, 0.4 mm, with marker windows | 0.7 |
| Round LiPo, 210 mAh | 4.1 |
| Board with nRF52840, SX1262, nRF9151, DW3110 and passives | 2.3 |
| UWB chip antenna | 0.1 |
| GPS/cellular antennas and strap contacts | 1.5 |
| Hand stepper + hands | 1.0 |
| Vibration motor | 0.8 |
| Crown, pusher, gaskets | 0.6 |
| Leather strap, 16 mm, 2.5 mm average | 5.5 |
| Titanium buckle | 1.2 |
| **Total** | **about 32** |

To reach about 29 g: 32 mm case (-1.5 g), 2.2 mm strap (-1 g), 0.8 mm crystal (-0.5 g).

## Prototype plan

The prototype uses dev boards, so it is bigger than the drawn watch (about 44 × 38 × 16 mm) and is worn on a wide strap. It proves the two buttons, UWB buddy radius, LoRa and cellular, not the finished size. Parts are in [`BOM.csv`](BOM.csv): about $247 and 49 g per prototype watch, most of it the UWB module ($59) and the cellular board (about $99). You need two watches to test the buddy radius.

1. Two XIAO nRF52840 + Wio-SX1262 stacks (one per test wearer), each with a DWM3001C UWB module on SPI.
2. One nRF9151 Feather for the cellular path on wearer A first; add to B once reports work.
3. Firmware: remap D1 (crown) to I'm Home with the 5 s cancel and D2 (pusher) to SOS with the 3 s hold and grace window; add UWB ranging and the radius and delay rules.
   **Pin check (found while planning this):** after the LoRa module, the XIAO has only 3 free pins (D0, D6, D7) plus 2 NFC pads. v1 already uses D0 for the button ladder, D6 for the motor and D7 for the LEDs, and v2 adds two UART links (UWB module and cellular board). The XIAO stack is 2 pins short. Two fixes, both off the shelf: swap the XIAO + Wio pair for a RAK4631 WisBlock core (the same nRF52840 + SX1262, with two UARTs and more GPIO), or let the DWM3001C's own nRF52833 drive the LED ring and motor. Decide before ordering.
4. Tests: UWB distance at 1/5/10/20/30 m in a bar and a hallway; separation alert timing at each delay; I'm Home and SOS from a basement over cellular; 6-mile report across boroughs.

## Sources

- Qorvo DW3110 package, current and channels (everything RF): https://www.everythingrf.com/products/rf-transceivers/qorvo/531-483-dw3110
- Qorvo DW3110 at Digi-Key: https://www.digikey.com/en/products/detail/qorvo/DW3110TR13/24717583
- Qorvo DWM3001C module (DW3110 + nRF52833, 27 × 19.13 × 3.2 mm, from $59.37): https://rfmw.com/products/detail/dwm3001c-qorvo/692453/
- Qorvo DWM3001C at Digi-Key: https://www.digikey.com/en/products/detail/qorvo/DWM3001CTR13/24367353
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
- Grepow round LiPo cells: https://grepow.com/battery-news/grepow-185mah-3-8v-round-shaped-lipo-battery-3030028.html
- Nordic DevZone, nRF9160 LTE-M current profile: https://devzone.nordicsemi.com/f/nordic-q-a/120415/nrf9160-lte-m-current-profile
- v1 watch feasibility, which this builds on: [`design/watch/FEASIBILITY.md`](../../design/watch/FEASIBILITY.md)
