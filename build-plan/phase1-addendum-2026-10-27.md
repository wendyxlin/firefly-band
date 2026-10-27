# Phase 1 addendum: Build plan edits of 2026-10-27

This answers the three "Last build plan edits" notes added to the Build plan doc on 2026-10-27. Phase 2 (hardware BOMs) has not been approved yet, so nothing in `hardware/`, `firmware/` or `ios/` was changed for the radio question. These are feasibility answers and decisions for Wendy.

## 1. "Update I'm safe to also add an I'm home button"

This is already built. Every output has a separate "I'm home" action next to "I'm okay" (the "I'm safe" check-in):

- Button 1: press 1x to find friends, 2x for "Come find me", **3x for "I'm home"**, hold for "I'm okay".
- The firmware sends HOME over LoRa and holds it for the wearer's phone, which then texts the contacts they chose. The iOS app, the phone app (`docs/app`), the concept page and the website all show it.

**Decision for Wendy:** keep "I'm home" as a triple-press (no new hardware), or add a **third physical button** just for it. A third button is easier to find at 2 a.m. but adds about 0.5 g, another seal to waterproof and more clutter on the jewelry. Our recommendation is to keep the triple-press, because the home press happens once, at the end of the night, usually somewhere calm.

Note: Tab 2 of the doc has a different button table (Button 2 single press = "I'm safe"). Tab 1, which the outputs follow, puts help and SOS on Button 2. The team should pick one table.

## 2. "Update LoRa radio to a longer GPS system for NYC to have range for miles"

Two corrections first:

- **GPS cannot carry messages.** It only receives satellite signals so the band knows where it is. It can't tell a friend anything. Range for miles needs a different *radio*, not more GPS.
- **LoRa is already the longest-range radio a bracelet can use to reach another bracelet directly.** Wrist to wrist in Manhattan, expect roughly 0.3-1 km at street level and 50-150 m inside a packed club. Your body absorbs signal, the antenna is tiny, and buildings block it. No legal low-power band-to-band radio gets you "miles" across NYC reliably.

Miles of range across the city needs **infrastructure** in between. There are three realistic ways to get it:

| Option | How it reaches miles | Added cost per band | Battery / weight | Privacy & other tradeoffs |
|---|---|---|---|---|
| **A. LTE-M cellular** (e.g. Nordic nRF9151, which also has GPS built in) | Uses carrier cell towers, so it works anywhere with LTE-M coverage | Module about $15-25 more than LoRa, plus data: 1NCE sells about 500 MB over 10 years for about $10 one-time | Needs about 20-40% more battery; about +2-3 g; a larger antenna is needed for the 700-800 MHz bands | Needs a SIM and a server to relay messages, so it isn't "no cloud" any more (messages can be end-to-end encrypted). Carrier certification (PTCRB/AT&T) costs time and money. Still weak in basements and the subway. |
| **B. Public LoRaWAN** (Helium / The Things Network gateways) | Keeps our LoRa radio; city gateways forward packets to the internet | About $0 in hardware; small data fees | No change | Messages go through the cloud and need an internet server. Reaching the band from the network is slow and limited, so this is good for "I'm home" and last-known location but poor for live finding. Coverage varies block by block. |
| **C. Home/rooftop relay** (a Firefly plug-in at one friend's apartment, Meshtastic style) | One high relay can cover about 1-3 miles of a neighborhood | About $30-40 per group | No change on the band | Still no cloud. Only covers that one neighborhood. Someone has to own it. |

**Recommendation:** keep LoRa for the night out itself (finding friends, help, SOS inside and near the venue). For the going-home problem, which is the one that needs miles, the most honest choice for a v1 that "just works" in NYC is **Option A (LTE-M)**. It is the only option that reaches someone in an Uber in another borough. It does break the "no subscription / no cloud" promise unless we bundle the 10-year data in the price, which we can do for about $10 per band. **Option B** is the cheapest way to try this in a class prototype, because it uses the same parts. This choice decides the Phase 2 BOM, so it needs Wendy's go-ahead.

## 3. "Waitlist and website won't open"

Root cause: **GitHub Pages was never switched on for the repo** (the repository reports `has_pages: false`), so `wendyxlin.github.io/firefly-band` returns "404". The page files in `docs/` are fine and load without script errors. Claude can't turn on Pages from here, so someone has to do it once in GitHub:

1. Open https://github.com/wendyxlin/firefly-band/settings/pages
2. Under **Build and deployment**, set **Source** to "Deploy from a branch", **Branch** to `main`, and **Folder** to `/docs`, then click **Save**.
3. Wait about 1-2 minutes, then open https://wendyxlin.github.io/firefly-band/ (the app is at `/app/`).

A `docs/.nojekyll` file was added so GitHub serves the files as-is. Also check the form: the "Firefly waitlist" Google Form is owned by an NYU account. If **Settings > Responses > "Restrict to users in NYU"** is on, people outside NYU are asked to sign in and the site's signups fail quietly. Turn that off so anyone can join the waitlist.

Until Pages is on, people can sign up through the Google Form directly:
https://docs.google.com/forms/d/e/1FAIpQLSeDMEhQfYmbDYZgqmqvd1ChsJuqbGd5-0xR9vZAamRsAIr4uA/viewform

## 4. New Tab 2 in the doc (competitor improvements, UWB)

Tab 2 suggests **BLE + UWB** as the starting point, with LoRa and GPS optional. This conflicts with Tab 1, which lists UWB as **out of scope for v1** and makes LoRa the core radio. Our honest take:

- UWB gives very good distance (about 10-30 cm) at **under 10-30 m, line of sight**. In a crowd it's blocked by bodies and has no range for the going-home problem. Real direction-finding needs 2-3 antennas, which won't fit in a jewelry centerpiece.
- A UWB module (e.g. Qorvo DWM3001C) adds about $15-20 and about 1-2 g, and needs its own power budget.
- It is a good *add-on* for the last 10 m of finding a friend, not a replacement for LoRa.

**Decision for Wendy:** keep Tab 1's plan (LoRa + BLE, UWB later) or add UWB in Phase 2. We recommend keeping UWB as a Phase 2 option to test, not a v1 requirement.
