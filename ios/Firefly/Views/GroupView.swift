import SwiftUI

struct GroupView: View {
    @EnvironmentObject var store: GroupStore

    var body: some View {
        List {
            if store.demoMode {
                Section {
                    Label("Demo mode: simulated bands. Pair a real band in My band.", systemImage: "sparkles")
                        .font(.footnote).foregroundStyle(.secondary)
                }
            }
            Section("Your group") {
                ForEach(store.friends.sorted { rank($0) > rank($1) }) { f in
                    NavigationLink(value: f.id) { FriendRow(friend: f) }
                }
            }
            Section {
                Button("Ping all bands", systemImage: "dot.radiowaves.left.and.right") { store.pingAll() }
                Button("Ask for check-in", systemImage: "checkmark.circle") { store.askCheckIn() }
            }
            if store.demoMode {
                Section("Demo: simulate a friend's band") {
                    Button("Jordan: come find me") { store.simulate(.comeFindMe, from: 1) }
                    Button("Priya: I'm okay") { store.simulate(.checkIn, from: 2) }
                    Button("Priya: I need help") { store.simulate(.help, from: 2) }
                    Button("Jordan: SOS", role: .destructive) { store.simulate(.sos, from: 1) }
                }
            }
        }
        .navigationTitle("Saturday night")
        .navigationDestination(for: UInt8.self) { id in NavigateView(friendID: id) }
    }

    private func rank(_ f: Friend) -> Int {
        switch f.status { case .sos: 4; case .help: 3; case .comeFindMe: 2; case .outOfRange: 1; case .ok: 0 }
    }
}

struct FriendRow: View {
    let friend: Friend
    var body: some View {
        HStack(spacing: 12) {
            ZStack(alignment: .bottomTrailing) {
                Circle().fill(Color(hex: friend.colorHex).opacity(0.2)).frame(width: 42, height: 42)
                    .overlay(Text(String(friend.name.prefix(1))).font(.headline).foregroundStyle(Color(hex: friend.colorHex)))
                Circle().fill(friend.status.color).frame(width: 12, height: 12).overlay(Circle().stroke(Color.night, lineWidth: 2))
            }
            VStack(alignment: .leading, spacing: 2) {
                Text(friend.name).font(.headline)
                Text("\(Int(friend.distance)) m · \(friend.link)").font(.caption.monospaced()).foregroundStyle(.secondary)
                Text("band \(friend.bandBattery)% · phone \(friend.phoneAlive ? "on" : "dead")").font(.caption2.monospaced()).foregroundStyle(.secondary)
            }
            Spacer()
            Text(friend.status.rawValue).font(.caption.bold())
                .padding(.horizontal, 8).padding(.vertical, 4)
                .background(friend.status.color.opacity(0.18), in: Capsule())
                .foregroundStyle(friend.status.color)
        }
        .padding(.vertical, 4)
    }
}
