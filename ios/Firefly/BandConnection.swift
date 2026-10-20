import Foundation
import CoreBluetooth
import Combine

/// Talks to the wearer's own band over Bluetooth LE.
/// The band is the bridge: it forwards LoRa packets from the rest of the group and sends the app's commands out.
final class BandConnection: NSObject, ObservableObject {
    enum State: Equatable { case off, unauthorized, idle, scanning, connecting, connected(name: String) }

    @Published private(set) var state: State = .idle
    @Published private(set) var bandBattery: Int?
    /// Called for every verified group packet the band forwards.
    var onPacket: ((GroupPacket) -> Void)?

    private var central: CBCentralManager!
    private var band: CBPeripheral?
    private var commandChar: CBCharacteristic?
    private let savedKey = "firefly.pairedBand"

    override init() {
        super.init()
        central = CBCentralManager(delegate: self, queue: .main, options: [CBCentralManagerOptionShowPowerAlertKey: true])
    }

    var isConnected: Bool { if case .connected = state { return true } else { return false } }

    /// Start pairing: scan for bands advertising the Firefly service. The band advertises fast while Button 1 is held.
    func startPairing() {
        guard central.state == .poweredOn else { return }
        state = .scanning
        central.scanForPeripherals(withServices: [FireflyProtocol.serviceUUID], options: [CBCentralManagerScanOptionAllowDuplicatesKey: false])
        DispatchQueue.main.asyncAfter(deadline: .now() + 20) { [weak self] in
            guard let self, self.state == .scanning else { return }
            self.central.stopScan(); self.state = .idle
        }
    }

    func forget() {
        if let band { central.cancelPeripheralConnection(band) }
        UserDefaults.standard.removeObject(forKey: savedKey)
        band = nil; state = .idle
    }

    func send(_ type: FireflyProtocol.MessageType, to target: UInt8 = 0xFF) {
        guard let band, let commandChar else { return }
        band.writeValue(GroupPacket.command(type, target: target), for: commandChar, type: .withResponse)
    }

    private func reconnectSaved() {
        guard let idString = UserDefaults.standard.string(forKey: savedKey), let id = UUID(uuidString: idString),
              let p = central.retrievePeripherals(withIdentifiers: [id]).first else { return }
        connect(p)
    }

    private func connect(_ p: CBPeripheral) {
        band = p; p.delegate = self; state = .connecting
        central.connect(p, options: nil) // iOS keeps this pending and reconnects when the band comes back in range
    }
}

extension BandConnection: CBCentralManagerDelegate {
    func centralManagerDidUpdateState(_ central: CBCentralManager) {
        switch central.state {
        case .poweredOn: state = .idle; reconnectSaved()
        case .unauthorized: state = .unauthorized
        default: state = .off
        }
    }

    func centralManager(_ central: CBCentralManager, didDiscover peripheral: CBPeripheral, advertisementData: [String: Any], rssi RSSI: NSNumber) {
        // Pair with the closest band only, so a friend's band across the room is not picked by mistake.
        guard RSSI.intValue > -60 else { return }
        central.stopScan()
        UserDefaults.standard.set(peripheral.identifier.uuidString, forKey: savedKey)
        connect(peripheral)
    }

    func centralManager(_ central: CBCentralManager, didConnect peripheral: CBPeripheral) {
        state = .connected(name: peripheral.name ?? "Firefly band")
        peripheral.discoverServices([FireflyProtocol.serviceUUID])
    }

    func centralManager(_ central: CBCentralManager, didDisconnectPeripheral peripheral: CBPeripheral, error: Error?) {
        state = .connecting
        central.connect(peripheral, options: nil)
    }
}

extension BandConnection: CBPeripheralDelegate {
    func peripheral(_ peripheral: CBPeripheral, didDiscoverServices error: Error?) {
        guard let s = peripheral.services?.first(where: { $0.uuid == FireflyProtocol.serviceUUID }) else { return }
        peripheral.discoverCharacteristics([FireflyProtocol.eventsUUID, FireflyProtocol.commandUUID, FireflyProtocol.rosterUUID], for: s)
    }

    func peripheral(_ peripheral: CBPeripheral, didDiscoverCharacteristicsFor service: CBService, error: Error?) {
        for c in service.characteristics ?? [] {
            switch c.uuid {
            case FireflyProtocol.eventsUUID, FireflyProtocol.rosterUUID: peripheral.setNotifyValue(true, for: c)
            case FireflyProtocol.commandUUID: commandChar = c
            default: break
            }
        }
    }

    func peripheral(_ peripheral: CBPeripheral, didUpdateValueFor characteristic: CBCharacteristic, error: Error?) {
        guard let data = characteristic.value else { return }
        if characteristic.uuid == FireflyProtocol.eventsUUID, let packet = GroupPacket(data: data) {
            onPacket?(packet)
        } else if characteristic.uuid == FireflyProtocol.rosterUUID, data.count >= 1 {
            bandBattery = Int(data[data.startIndex])
            // Bytes after the first are [id, rssi, battery] triples for every band heard in the last 10 s.
            let b = [UInt8](data.dropFirst())
            for i in stride(from: 0, to: b.count - 2, by: 3) {
                onPacket?(GroupPacket(type: .checkIn, from: b[i], rssi: Int8(bitPattern: b[i + 1])).withBattery(b[i + 2]).markedAsRoster())
            }
        }
    }
}

private extension GroupPacket {
    func withBattery(_ v: UInt8) -> GroupPacket { var p = self; p.battery = v; return p }
    /// Roster updates reuse the packet type with seq 0 so the store treats them as presence, not as a check-in event.
    func markedAsRoster() -> GroupPacket { var p = self; p.seq = 0; return p }
}
