# Firefly iOS app (SwiftUI)

Native app for the "responsible friend": pairs with your band over Bluetooth, shows the group on a map, points you to a friend with a live compass, and raises full-screen help/SOS alerts. With no band paired, it runs a built-in demo with three simulated friends so you can try every screen.

**Status:** source code, written to match the firmware in `../firmware`. Not yet compiled or run on a device, so expect small fixes the first time you build it in Xcode.

## Run it on your iPhone (free, no App Store)

You need a Mac with **Xcode 15 or later** and an iPhone on iOS 17+. A free Apple ID works; a paid developer account is only needed for TestFlight or the App Store.

**Option A: XcodeGen (fastest)**
1. `brew install xcodegen`
2. `cd ios && xcodegen`. This creates `Firefly.xcodeproj`.
3. Open it, select the **Firefly** target → *Signing & Capabilities* → pick your Team (your Apple ID) and change the bundle id to something unique, e.g. `com.yourname.firefly`.
4. Plug in your iPhone, choose it as the run destination, press **Run** (⌘R).
5. On the phone: *Settings → General → VPN & Device Management* → trust your developer certificate. On iOS 16+ also turn on *Settings → Privacy & Security → Developer Mode*.

**Option B: by hand**
1. Xcode → *File → New → Project → iOS App*, name it **Firefly**, interface **SwiftUI**.
2. Delete the generated `ContentView.swift` and `FireflyApp.swift`, then drag everything in `ios/Firefly/` into the project.
3. In the target's *Info* tab add:
   - `NSBluetoothAlwaysUsageDescription`: "Firefly connects to your band over Bluetooth."
   - `NSLocationWhenInUseUsageDescription`: "Firefly uses your location to place friends on the map."
4. *Signing & Capabilities* → **+ Capability → Background Modes** → tick **Uses Bluetooth LE accessories**.
5. Run on your phone as in steps 3–5 above.

Free-account apps expire after 7 days. Press Run again to refresh.

## Sharing with your team

- **TestFlight** (needs the $99/yr Apple Developer Program): *Product → Archive → Distribute App → TestFlight*, then invite testers by email. This is how the team gets an app they can download.
- **Today, with no Mac:** the web version of the app works on any phone. Open the link in Safari and tap *Share → Add to Home Screen*.

## How it talks to the band

| File | What it does |
|---|---|
| `FireflyProtocol.swift` | GATT UUIDs and the 12-byte packet layout shared with the firmware |
| `BandConnection.swift` | CoreBluetooth: scan, pair with the closest band, auto-reconnect, receive packets, send commands |
| `GroupStore.swift` | The night's state: friends, distances (RSSI → metres), events, alerts, demo simulation, GPS and compass heading |
| `Views/` | Group, Map, Navigate, Alerts, My band, Privacy, full-screen SOS |
