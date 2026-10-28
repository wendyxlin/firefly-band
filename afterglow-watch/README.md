# Afterglow watch: the two-button watch direction

**Stay close. Go out.** The watch direction of the Firefly concept (built as v2 on 2026-10-27, then moved here when the team picked the bracelet board for v2), following the team's Afterglow demo (`afterglow_demo.html` in the shared Drive folder). It's a 34 mm dress watch with only two buttons:

| Button | What it does |
|---|---|
| **Crown, 3 o'clock: I'm Home** | Press to tell your circle you're home. Press again within 5 s to cancel. Two short buzzes, then the dial sweeps green when it's delivered. |
| **Red-ringed pusher, 2 o'clock: SOS** | Hold 3 s. Your circle and your backup contact get your live location. Press twice during the 5–10 s grace window to cancel. The dial pulses red. |

Everything else is either automatic or in the app:
- **Separation alerts (automatic).** You pick a buddy radius of 10–30 m and an alert delay of 1, 2 or 5 min. Drift outside the radius and the watch buzzes; the marker toward your circle glows lavender.
- **Finding a friend and Come Find Me (app).** Finding shows the distance between watches from ultra-wideband (UWB), with no map or arrow up close.
- **Who's home (app).** A list of check-ins, with a nudge for anyone you're still waiting on.

Range is **at least 6 miles, even with weak signal**:
- UWB covers 0–30 m.
- LoRa covers 30 m–1 km.
- Built-in LTE-M/NB-IoT cellular covers 1 km to 6+ miles.
- Amazon Sidewalk and Find My / Find Hub are fallbacks.

This is one of two designs presented at Sprint 2. The v2 bracelet is in [`v2-bracelet/`](../v2-bracelet/).

## What's in this folder

| Path | What it is |
|---|---|
| [`index.html`](index.html) | Website: hero, film, the two buttons, app features, range, design renders, privacy, waitlist (same Google Form as v1), FAQ |
| [`app/`](app/) | Installable phone web app (PWA) based on the demo: Home, Friends, Check-ins and Settings tabs, a watch simulator with both buttons, and Web Bluetooth pairing |
| [`mockup/`](mockup/) | Interactive 3D design review: turn the watch, switch dial states (idle, apart, I'm Home, SOS), finishes and straps, X-ray and exploded views |
| [`renders/`](renders/) | Blender Cycles renders with physically based materials, plus app screenshots |
| [`media/afterglow-promo.mp4`](media/afterglow-promo.mp4) | 68 s promo film, 1080p, with sound |
| [`technical/TECHNICAL_DESIGN.md`](technical/TECHNICAL_DESIGN.md) | Two-button firmware map, range stack, feasibility checks, battery and weight budgets, sources |
| [`technical/BOM.csv`](technical/BOM.csv) | Prototype parts list with prices and links (about $247 per watch) |
| [`source/`](source/) | Scripts that make the renders and the film (three.js → OBJ → Blender, canvas → ffmpeg) |

Hosted copy for GitHub Pages: [`docs/afterglow-watch/`](../docs/afterglow-watch/) → https://wendyxlin.github.io/firefly-band/afterglow-watch/ once Pages is enabled.

## Feasibility in one paragraph

Every part exists today. Compared with the v1 watch, v2 changes the button firmware and adds a Qorvo DW3110 UWB chip (3.1 × 3.5 mm, about 0.9 g and 0.2 mA with its antenna). With a 210 mAh cell that's about 13 h on a heavy night. Open items:
- The design is about 32 g as drawn; the target is about 29 g.
- The dial needs light windows under the markers.
- The glowing marker can only point toward your circle outdoors. Indoors the watch pulses all the markers instead.
- The XIAO prototype stack is 2 pins short for the new UWB and cellular links. The technical doc gives two fixes.

Details and sources are in the [technical design](technical/TECHNICAL_DESIGN.md).

## Not yet done for v2

- Firmware and the iOS app still implement the v1 button mapping (in `firmware/` and `ios/`). The v2 mapping is specified in the technical doc.
- No printable STL for the watch case yet.
