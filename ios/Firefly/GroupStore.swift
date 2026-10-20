import Foundation
import CoreLocation
import Combine
import UIKit

struct Friend: Identifiable, Equatable {
    enum Status: String { case ok = "okay", comeFindMe = "come find me", help = "needs help", sos = "SOS", outOfRange = "out of range" }
    let id: UInt8
    var name: String
    var colorHex: UInt32
    var coordinate: CLLocationCoordinate2D   // estimated from signal relative to the phone
    var distance: Double                      // metres from the phone
    var bandBattery: Int
    var phoneAlive: Bool
    var status: Status = .ok
    var lastCheckIn: Date = .now
    var isHelpContact = true

    static func == (a: Friend, b: Friend) -> Bool { a.id == b.id && a.distance == b.distance && a.status == b.status && a.bandBattery == b.bandBattery }
    var link: String { distance < 25 ? "Bluetooth" : distance < 300 ? "LoRa" : "out of range" }
    var bars: Int { distance < 5 ? 4 : distance < 12 ? 3 : distance < 25 ? 2 : distance < 300 ? 1 : 0 }
}

struct GroupEvent: Identifiable {
    enum Kind { case ok, find, help, sos }
    let id = UUID()
    let kind: Kind
    let friendID: UInt8?
    let text: String
    let time: Date = .now
}

/// The whole night: who is in the group, where they are, and what happened.
/// Runs on real band data when a band is connected, or on a built-in demo otherwise.
@MainActor
final class GroupStore: NSObject, ObservableObject {
    @Published var friends: [Friend] = []
    @Published var events: [GroupEvent] = []
    @Published var myLocation = CLLocationCoordinate2D(latitude: 40.7301, longitude: -73.9978) // Washington Sq, until GPS arrives
    @Published var heading: CLLocationDirection = 0
    @Published var activeAlert: Friend?
    @Published var demoMode = true
    @Published var sessionEnds = Calendar.current.nextDate(after: .now, matching: DateComponents(hour: 6), matchingPolicy: .nextTime) ?? .now
    @Published var shareGPS = true
    @Published var keepHistory = false
    @Published var cloudRelay = false

    let band = BandConnection()
    private let location = CLLocationManager()
    private var demoTimer: Timer?
    private var bag = Set<AnyCancellable>()

    override init() {
        super.init()
        location.delegate = self
        location.desiredAccuracy = kCLLocationAccuracyBest
        band.onPacket = { [weak self] p in Task { @MainActor in self?.handle(p) } }
        band.$state.sink { [weak self] s in
            guard let self else { return }
            if case .connected = s { self.stopDemo() }
        }.store(in: &bag)
        startDemo()
    }

    func requestPermissions() {
        location.requestWhenInUseAuthorization()
        location.startUpdatingLocation()
        if CLLocationManager.headingAvailable() { location.startUpdatingHeading() }
    }

    // MARK: Actions from the UI
    func ping(_ f: Friend) {
        band.send(.ping, to: f.id)
        log(.find, f.id, "You pinged \(f.name)'s band: 3 buzzes, light on for 10 s")
    }
    func pingAll() { band.send(.ping); log(.find, nil, "Pinged every band in range") }
    func askCheckIn() {
        band.send(.askCheckIn); log(.find, nil, "Asked the group to check in")
        if demoMode { DispatchQueue.main.asyncAfter(deadline: .now() + 2) { self.simulate(.checkIn, from: 2) } }
    }
    func sendAsMe(_ t: FireflyProtocol.MessageType) {
        band.send(t)
        let text: String = switch t { case .checkIn: "You checked in: I'm okay"; case .comeFindMe: "You sent \"Come find me\""; case .help: "You sent a discreet \"I need help\""; case .sos: "You sent an SOS"; default: "Sent" }
        log(t == .sos ? .sos : t == .help ? .help : .ok, nil, text)
    }
    func resolve(_ f: Friend) {
        update(f.id) { $0.status = .ok; $0.lastCheckIn = .now }
        band.send(.cancel, to: f.id)
        log(.ok, f.id, "Alert cleared: \(f.name) found and okay")
        if activeAlert?.id == f.id { activeAlert = nil }
    }
    func endNight() {
        band.send(.leave)
        events.removeAll(); friends.removeAll(); activeAlert = nil
    }

    // MARK: Incoming packets
    func handle(_ p: GroupPacket) {
        if !friends.contains(where: { $0.id == p.from }) {
            friends.append(Friend(id: p.from, name: "Band \(p.from)", colorHex: 0xC9A0FF, coordinate: myLocation, distance: 30, bandBattery: Int(p.battery), phoneAlive: false))
        }
        if p.rssi != 0 {
            let d = estimatedDistance(rssi: Int(p.rssi))
            update(p.from) { $0.distance = d; if p.battery > 0 { $0.bandBattery = Int(p.battery) } }
        }
        guard p.seq != 0, let f = friends.first(where: { $0.id == p.from }) else { return } // seq 0 = presence only
        switch p.type {
        case .checkIn: update(f.id) { $0.status = .ok; $0.lastCheckIn = .now }; log(.ok, f.id, "\(f.name) checked in: I'm okay")
        case .comeFindMe: update(f.id) { $0.status = .comeFindMe }; log(.find, f.id, "\(f.name): come find me"); haptic(.warning)
        case .help: update(f.id) { $0.status = .help }; log(.help, f.id, "\(f.name) needs help"); raise(f.id)
        case .sos: update(f.id) { $0.status = .sos }; log(.sos, f.id, "\(f.name): SOS"); raise(f.id)
        case .cancel: update(f.id) { $0.status = .ok }; log(.ok, f.id, "\(f.name) cancelled the alert"); if activeAlert?.id == f.id { activeAlert = nil }
        case .leave: log(.help, f.id, "\(f.name) left the group"); friends.removeAll { $0.id == f.id }
        default: break
        }
    }

    private func raise(_ id: UInt8) { activeAlert = friends.first { $0.id == id }; haptic(.error) }
    private func haptic(_ t: UINotificationFeedbackGenerator.FeedbackType) { UINotificationFeedbackGenerator().notificationOccurred(t) }
    private func update(_ id: UInt8, _ change: (inout Friend) -> Void) { if let i = friends.firstIndex(where: { $0.id == id }) { change(&friends[i]) } }
    private func log(_ k: GroupEvent.Kind, _ id: UInt8?, _ text: String) { events.insert(GroupEvent(kind: k, friendID: id, text: text), at: 0) }

    // MARK: Geometry
    func bearing(to f: Friend) -> Double {
        let lat1 = myLocation.latitude * .pi / 180, lat2 = f.coordinate.latitude * .pi / 180
        let dLon = (f.coordinate.longitude - myLocation.longitude) * .pi / 180
        let y = sin(dLon) * cos(lat2), x = cos(lat1) * sin(lat2) - sin(lat1) * cos(lat2) * cos(dLon)
        return (atan2(y, x) * 180 / .pi + 360).truncatingRemainder(dividingBy: 360)
    }
    func compassLetter(_ deg: Double) -> String { ["N","NE","E","SE","S","SW","W","NW"][Int((deg + 22.5) / 45) % 8] }
    private func offset(_ c: CLLocationCoordinate2D, east: Double, north: Double) -> CLLocationCoordinate2D {
        CLLocationCoordinate2D(latitude: c.latitude + north / 111_111, longitude: c.longitude + east / (111_111 * cos(c.latitude * .pi / 180)))
    }

    // MARK: Demo mode (no hardware yet)
    private var demoOffsets: [UInt8: (Double, Double)] = [1: (24, -9), 2: (13, 5), 3: (78, -38)]
    func startDemo() {
        demoMode = true
        friends = [
            Friend(id: 1, name: "Jordan", colorHex: 0xF5B544, coordinate: myLocation, distance: 26, bandBattery: 71, phoneAlive: false),
            Friend(id: 2, name: "Priya", colorHex: 0xC9A0FF, coordinate: myLocation, distance: 14, bandBattery: 64, phoneAlive: true),
            Friend(id: 3, name: "Sam", colorHex: 0x6FA8FF, coordinate: myLocation, distance: 87, bandBattery: 45, phoneAlive: false, isHelpContact: false),
        ]
        recomputeDemo()
        demoTimer?.invalidate()
        demoTimer = Timer.scheduledTimer(withTimeInterval: 1.5, repeats: true) { [weak self] _ in
            Task { @MainActor in
                guard let self else { return }
                for (k, v) in self.demoOffsets where k != 3 { self.demoOffsets[k] = (v.0 + .random(in: -0.8...0.8), v.1 + .random(in: -0.8...0.8)) }
                self.recomputeDemo()
            }
        }
    }
    private func recomputeDemo() {
        for i in friends.indices {
            guard let o = demoOffsets[friends[i].id] else { continue }
            friends[i].coordinate = offset(myLocation, east: o.0, north: o.1)
            friends[i].distance = hypot(o.0, o.1)
            if friends[i].distance > 300 { friends[i].status = .outOfRange }
        }
    }
    func stopDemo() { demoTimer?.invalidate(); demoMode = false; friends.removeAll(); events.removeAll() }
    func simulate(_ t: FireflyProtocol.MessageType, from id: UInt8) { handle(GroupPacket(type: t, from: id, seq: UInt16.random(in: 1...60000))) }
    func simulateWalkToward(_ f: Friend) {
        guard let o = demoOffsets[f.id] else { return }
        demoOffsets[f.id] = (o.0 * 0.8, o.1 * 0.8); recomputeDemo()
    }
}

extension GroupStore: CLLocationManagerDelegate {
    nonisolated func locationManager(_ manager: CLLocationManager, didUpdateLocations locations: [CLLocation]) {
        guard let c = locations.last?.coordinate else { return }
        Task { @MainActor in self.myLocation = c; if self.demoMode { self.recomputeDemo() } }
    }
    nonisolated func locationManager(_ manager: CLLocationManager, didUpdateHeading newHeading: CLHeading) {
        let h = newHeading.trueHeading >= 0 ? newHeading.trueHeading : newHeading.magneticHeading
        Task { @MainActor in self.heading = h }
    }
}
