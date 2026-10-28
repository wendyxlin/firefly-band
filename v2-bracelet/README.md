# Firefly v2: the bracelet

**Stay connected. Go further together.** Version 2 follows the team's design board: a slim bangle with a soft capsule on top that carries two round buttons and one pinhole light. It comes in gold, silver, rose gold and black.

| Input | What it does |
|---|---|
| **Button 1** (engraved dot), press | Find friends. It buzzes, and the light pulses faster as you get closer. |
| **Button 1**, press twice | Come find me. Your group's bracelets buzz twice. |
| **Button 2** (engraved line), press | I'm home. The light turns green when it's delivered. Press twice within 5 s to cancel. |
| **Both buttons**, hold 3 s | Quiet SOS to your group and a backup contact, after a 5–10 s grace window. Press either button twice to cancel. |
| Automatic | Separation alert. Pick a radius of 10, 20 or 30 m and a delay of 1, 2 or 5 min. |

Range is **at least 6 miles, even with weak signal**. Each distance band uses a different link:
- 0–30 m: ultra-wideband (UWB)
- 30 m–1 km: LoRa
- 1 km to 6+ miles: built-in LTE-M/NB-IoT cellular
- Fallbacks: Amazon Sidewalk, plus Find My or Find Hub

## What's in this folder

| Path | What it is |
|---|---|
| [`index.html`](index.html) | Website. Includes lifestyle shots from the design board, renders, the app, range, colour options, the waitlist (same Google Form as v1) and an FAQ. |
| [`app/`](app/) | Installable phone web app. Tabs: My Group, Find Friends ("Getting closer… 3 meters away"), Check-ins and Settings. Includes a bracelet simulator for every gesture, Web Bluetooth pairing and an SOS backup contact. |
| [`mockup/`](mockup/) | Interactive 3D design review. Switch states (find, come find me, home, separated, SOS) and colours, and use the wrist, X-ray and Explode views. |
| [`renders/`](renders/) | Blender Cycles renders, crops from the design board, and app screenshots. |
| [`media/firefly-v2-promo.mp4`](media/firefly-v2-promo.mp4) | 68 s promo film, 1080p, with sound. |
| [`technical/TECHNICAL_DESIGN.md`](technical/TECHNICAL_DESIGN.md) | Button map, hardware layout, range stack, feasibility checks, battery and weight budgets, and sources. |
| [`technical/BOM.csv`](technical/BOM.csv) | Prototype parts list. About $247 per bracelet. |
| [`source/`](source/) | Scripts that make the renders and the film. |

The hosted copy for GitHub Pages is in [`docs/v2-bracelet/`](../docs/v2-bracelet/). Once Pages is enabled, it's at https://wendyxlin.github.io/firefly-band/v2-bracelet/.

The Sprint 2 decks are in [`presentations/sprint2/`](../presentations/sprint2/). There is one for this bracelet and one for the [Afterglow watch](../afterglow-watch/).

## Feasibility in one paragraph

Every part exists today. Battery space is the main constraint:
- An 85 mAh cell fits in the capsule. On its own it gives about 5 h on a heavy night.
- A second 60 mAh cell in the slim clasp under the wrist brings it to about 9 h.
- Weight is about 15 g in titanium.
- The metal band doubles as the LoRa and cellular antenna. That still needs RF tuning on real wrists.
- UWB has to leave through the capsule's ceramic underside.

Details and sources are in the [technical design](technical/TECHNICAL_DESIGN.md).

## Not yet done for v2

- The firmware and iOS app in `firmware/` and `ios/` still implement the v1 gestures. The v2 map is specified in the technical doc.
- There's no printable STL for the capsule yet.
