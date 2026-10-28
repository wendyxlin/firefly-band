# Phase 1 addendum: Build plan edits of 2026-10-28

The doc changed at 2026-10-28 01:44 UTC. **Tab 1 is unchanged.** **Tab 2 was replaced**: the old "Can you use their technology and improve the product?" text (four improvements, Totem comparison) is gone, and in its place is a proposal built around an automatic **separation alert**.

Phase 1 (feasibility) is still waiting for Wendy's approval, so this is a feasibility answer only. The concept page, phone app, website, firmware, iOS app and hardware files were **not** changed. Each item below says what it would change once the next phase is approved.

## What the new Tab 2 proposes

| Feature | Button / trigger | Radio named in Tab 2 | Today in the repo (Tab 1 plan) |
|---|---|---|---|
| Find Friends | Button 1 × 1. **LED only**, blinks faster as you get closer (the find vibration is removed) | UWB | Button 1 × 1, LED **and** haptic pulse, LoRa signal strength |
| Come Find Me | Button 1 × 2, friends get two vibrations | Bluetooth | Same gesture, sent over LoRa |
| I'm Home | **Button 2 × 1** | Bluetooth + app/internet | Button 1 × 3 |
| Separation alert ⭐ | Automatic: radius 10/20/30 m, 1-3 min delay, pause, per-person opt-in, measured from a **designated buddy** | UWB + Bluetooth | Not built. The app only shows "out of range" when a band drops out of LoRa range |
| Companion app | Group Safety Dashboard: Nearby / Outside selected radius / Connection lost / I'm Home | Phone | Map, compass, alert feed, roll call |
| Hardware | 2 buttons, 1 LED, 1 vibration motor, UWB, Bluetooth, battery | No LoRa, no GPS | LoRa + BLE, 2 buttons, LED, haptic |

**Not in the new Tab 2:** "I need help", cancel, SOS, "I'm okay", stillness alert, SOS escalation, and LoRa. Tab 1 still requires all of them.

## Honest feasibility

**1. The separation alert is feasible, and it is the best idea in the new tab.** It works with no button press, so it helps the friend who doesn't realize they've drifted off. Measuring from one designated buddy is the right call. Each band ranges to one partner instead of every pair (a group of 5 would need 10 pairs), which keeps power use and radio traffic low.

**2. UWB distance is accurate, but its range in a packed club is short.** Line of sight, UWB measures distance to about 10-30 cm. On a wrist in a crowd, bodies block the 6.5-8 GHz signal. Expect reliable readings out to roughly 10-20 m and frequent dropouts beyond that. In practice:
- **10 m and 20 m settings are realistic.**
- **30 m is at the edge.** Above about 20 m, "outside your radius" and "connection lost" will often look the same. The app should treat a dropout lasting longer than the alert delay as a separation, and word it the way Tab 2 does ("Connection with Emma lost, last detected 2 min ago").
- Bluetooth signal strength is too noisy to set a 10/20/30 m line by itself (readings vary by several metres). Use it only as a backup.

**3. Bluetooth alone can't carry "Come find me" or "I'm Home" far enough.** Wrist to wrist, Bluetooth reaches about 10-30 m in a crowded club. "Come find me" matters most when your friends are *not* nearby, and "I'm Home" is sent from home, miles from the group. If LoRa is dropped as Tab 2 suggests:
- "Come find me" only reaches friends who are already close.
- "I'm Home" only gets through if the wearer's own phone is charged and online. That breaks the core promise for the friend whose phone is dead.

**Recommendation:** keep LoRa for messages and add UWB for distance. Tab 2's feature list works on that combination; it doesn't work on Bluetooth + UWB alone. The miles-range question from the 2026-10-27 addendum (LTE-M, Sidewalk or a home relay) is still open and is what really fixes "I'm Home".

**4. "I'm Home" on a single press of Button 2 is risky.** A single press is the easiest gesture to trigger by accident: bumping the bar, a hug, a purse strap. A false "I'm Home" tells the group you're safe while you're still out, and it does that silently. Recommendation: keep "I'm Home" on a deliberate gesture (a triple-press, or a 2 s hold with a confirming buzz). Keep Button 2 hold-3 s for SOS, which Tab 1 requires.

**5. LED-only finding is fine and saves a little power.** One caveat: under club lights, a small LED behind a stone is hard to see, and you have to look at your wrist. Keep one short buzz when you reach your friend, or leave it as a setting. The separation alert still needs its own vibration pattern for dead-phone wearers, as Tab 2 says.

**6. UWB parts: cost, size and metal.** These figures correct the 2026-10-27 addendum, which guessed "about $15-20".
- **Qorvo DWM3001C** module (UWB + Bluetooth MCU + antenna, pre-built): **$59.37 each at 1-24, $43.18 at 100-249** on the Qorvo store; **27 × 19.1 × 3.2 mm**. It has a Bluetooth chip inside (nRF52833), so in a prototype it can replace the XIAO nRF52840 instead of adding a board. It is too big for the current centerpiece, though, and fits the watch case or a dev-board prototype better.
- For production, a chip-down DW3000-series design on our own board would be smaller and cheaper. Get a quote in Phase 2.
- **Radio through metal:** UWB at 6.5-8 GHz won't pass through the gold-plated brass or titanium case. The UWB antenna has to sit behind a non-metal window. The opalite stone (bangle) or the crystal/dial (watch) could be that window. This must be tested on a real wrist.
- Power: ranging with one buddy every 1-2 s adds roughly 0.3-1 mA on average. That fits the Phase 1 budget (typical night 3.5 mA), but it must be measured on hardware.
- Weight: about +1-2 g with a chip-down design. The bangle (~22 g) has room. The watch (~31 g) is already over 30 g.
- Regulation: UWB in the US falls under FCC Part 15 Subpart F (handheld rules in §15.519), and in the EU under ETSI EN 302 065. Use a pre-certified module for the prototype.

**7. Privacy.** A radius alert feels more like monitoring than a button press does. Tab 2's per-person opt-in and pause match Tab 1's consent rules. Add: an alert only goes to the buddy and the organizer, not the whole group, and the setting turns off when the group session ends.

## Decisions for Wendy (in order)

1. **Approve Phase 1** (still pending), so Phase 2 (hardware BOM) can start.
2. **Which tab rules the feature list?** Tab 2 drops help, cancel, SOS, "I'm okay" and LoRa. Our recommendation: Tab 1's safety features **plus** Tab 2's separation alert.
3. **Add UWB in Phase 2?** Tab 1 lists it as out of scope for v1; Tab 2 makes it essential. Our recommendation: yes, as the buddy-distance sensor, alongside LoRa. Prototype it with the DWM3001C.
4. **The "I'm Home" gesture:** a single press of Button 2 (Tab 2) or a deliberate gesture (our recommendation).
5. **Separation defaults:** buddy-based, 20 m default, 2 min delay, with 10 m and 30 m offered as options (labelled "approximate").

## What changes in the repo once these are approved

- **Phase 2:** BOM.csv and BUILD.md add the UWB module; the firmware gets a ranging loop and a SEPARATION message type (already in Tab 1's packet list).
- **Phase 5:** the app adds a radius and delay picker, buddy selection, and the Nearby / Outside radius / Connection lost / I'm Home dashboard. The website and concept page get the updated feature list.

## Sources

- Qorvo store, DWM3001C price and package size: https://store.qorvo.com/products/detail/dwm3001c-qorvo/692453/
- Digi-Key listing, DWM3001CTR13: https://www.digikey.com/en/products/detail/qorvo/DWM3001CTR13/24367353
