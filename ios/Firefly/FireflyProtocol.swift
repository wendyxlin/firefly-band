import Foundation
import CoreBluetooth

/// Shared definitions between the iOS app and the band firmware (firmware/firefly/firefly.ino).
/// Keep these UUIDs and byte layouts in sync with the firmware.
enum FireflyProtocol {
    /// Custom GATT service advertised by every band.
    static let serviceUUID = CBUUID(string: "F1F1A000-7C3B-4E2A-9A1D-5B0E46F1F1F1")
    /// Notify: events relayed from the group (12-byte packets, see `GroupPacket`).
    static let eventsUUID  = CBUUID(string: "F1F1A001-7C3B-4E2A-9A1D-5B0E46F1F1F1")
    /// Write: commands from the app to the band (ping a friend, ask for check-in, send as me).
    static let commandUUID = CBUUID(string: "F1F1A002-7C3B-4E2A-9A1D-5B0E46F1F1F1")
    /// Read/notify: roster of band ids the band currently hears, with RSSI and battery.
    static let rosterUUID  = CBUUID(string: "F1F1A003-7C3B-4E2A-9A1D-5B0E46F1F1F1")

    enum MessageType: UInt8 {
        case checkIn = 1, comeFindMe = 2, help = 3, sos = 4, cancel = 5, ping = 6, leave = 7, askCheckIn = 8, join = 9, home = 10
    }
}

/// 12-byte packet the bands exchange over LoRa and the band forwards to the phone.
/// Layout (little endian): magic(1)=0xF1, type(1), from(1), hops(1), seq(2), battery(1), rssi(1, signed), mac(4)
struct GroupPacket: Equatable {
    var type: FireflyProtocol.MessageType
    var from: UInt8
    var seq: UInt16
    var battery: UInt8
    var rssi: Int8

    init?(data: Data) {
        guard data.count >= 12, data[data.startIndex] == 0xF1,
              let t = FireflyProtocol.MessageType(rawValue: data[data.startIndex + 1]) else { return nil }
        let b = [UInt8](data)
        type = t
        from = b[2]
        seq = UInt16(b[4]) | (UInt16(b[5]) << 8)
        battery = b[6]
        rssi = Int8(bitPattern: b[7])
        // b[8...11] is the truncated HMAC. The band verifies it before forwarding.
    }

    init(type: FireflyProtocol.MessageType, from: UInt8, seq: UInt16 = 0, battery: UInt8 = 0, rssi: Int8 = 0) {
        self.type = type; self.from = from; self.seq = seq; self.battery = battery; self.rssi = rssi
    }

    /// Command written to the band: [type, targetId]. targetId 0xFF = everyone.
    static func command(_ type: FireflyProtocol.MessageType, target: UInt8 = 0xFF) -> Data {
        Data([type.rawValue, target])
    }
}

/// Rough distance from Bluetooth RSSI using a log-distance path-loss model.
/// txPower is the RSSI measured at 1 m (calibrate per band; about -59 dBm for the XIAO at 0 dBm).
func estimatedDistance(rssi: Int, txPower: Int = -59, pathLoss: Double = 2.7) -> Double {
    guard rssi < 0 else { return 0.5 }
    return pow(10.0, Double(txPower - rssi) / (10.0 * pathLoss))
}
