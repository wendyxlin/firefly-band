import SwiftUI

struct AlertsView: View {
    @EnvironmentObject var store: GroupStore
    var body: some View {
        List {
            if store.events.isEmpty {
                ContentUnavailableView("Quiet so far", systemImage: "moon.stars", description: Text("Check-ins and alerts from your group show up here."))
            }
            ForEach(store.events) { e in
                HStack(alignment: .top, spacing: 10) {
                    RoundedRectangle(cornerRadius: 2).fill(color(e.kind)).frame(width: 4)
                    VStack(alignment: .leading, spacing: 2) {
                        Text(e.time, style: .time).font(.caption2.monospaced()).foregroundStyle(.secondary)
                        Text(e.text)
                    }
                    Spacer()
                    if let id = e.friendID, e.kind != .ok {
                        NavigationLink("Go", value: id).font(.caption.bold()).fixedSize()
                    }
                }
            }
        }
        .navigationTitle("Tonight")
        .navigationDestination(for: UInt8.self) { id in NavigateView(friendID: id) }
    }
    private func color(_ k: GroupEvent.Kind) -> Color { switch k { case .ok: .green; case .find: .blue; case .help: .orange; case .sos: .red } }
}

struct BandView: View {
    @EnvironmentObject var store: GroupStore
    var body: some View {
        List {
            Section("Connection") {
                switch store.band.state {
                case .connected(let name):
                    LabeledContent(name, value: "connected")
                    if let b = store.band.bandBattery { LabeledContent("Band battery", value: "\(b)%") }
                    Button("Forget this band", role: .destructive) { store.band.forget(); store.startDemo() }
                case .scanning:
                    HStack { ProgressView(); Text("Hold Button 1 on your band for 3 seconds…") }
                case .connecting:
                    HStack { ProgressView(); Text("Reconnecting to your band…") }
                case .off:
                    Text("Turn on Bluetooth to pair your band.")
                case .unauthorized:
                    Text("Allow Bluetooth for Firefly in Settings to pair your band.")
                case .idle:
                    Button("Pair my band", systemImage: "dot.radiowaves.left.and.right") { store.band.startPairing() }
                }
            }
            Section("Send from my band") {
                Button("I'm okay") { store.sendAsMe(.checkIn) }
                Button("Come find me") { store.sendAsMe(.comeFindMe) }
                Button("I need help") { store.sendAsMe(.help) }.foregroundStyle(.orange)
                Button("SOS", role: .destructive) { store.sendAsMe(.sos) }
                Button("I'm home") { store.imHome() }
            }
            HomeTextSettings()
            Section("Button guide") {
                Text("**Button 1 · Find**\n1× find friends · 2× come find me · 3× I'm home · hold: I'm okay")
                Text("**Button 2 · Safety** (dimpled)\n1× discreet help · 2× cancel · hold 3 s: SOS")
                Text("**Both, 5 s:** leave the group")
            }
            .font(.subheadline)
        }
        .navigationTitle("My band")
    }
}

struct PrivacyView: View {
    @EnvironmentObject var store: GroupStore
    @State private var confirmEnd = false
    var body: some View {
        Form {
            Section {
                Toggle(isOn: $store.shareGPS) { VStack(alignment: .leading) { Text("Share my GPS with the group"); Text("Only during this session").font(.caption).foregroundStyle(.secondary) } }
                Toggle(isOn: $store.keepHistory) { VStack(alignment: .leading) { Text("Keep a location history"); Text("Off: tonight's trail is wiped at session end").font(.caption).foregroundStyle(.secondary) } }
                Toggle(isOn: $store.cloudRelay) { VStack(alignment: .leading) { Text("Cloud relay for alerts"); Text("Off: nothing leaves the phones and bands").font(.caption).foregroundStyle(.secondary) } }
            }
            Section("Who gets \"I need help\"") {
                ForEach($store.friends) { $f in Toggle(f.name, isOn: $f.isHelpContact) }
            }
            Section("Session") {
                LabeledContent("Ends", value: store.sessionEnds.formatted(date: .omitted, time: .shortened))
                Button("Extend 1 hour") { store.sessionEnds.addTimeInterval(3600) }
                Button("End night now", role: .destructive) { confirmEnd = true }
            }
        }
        .navigationTitle("Privacy")
        .confirmationDialog("End the night?", isPresented: $confirmEnd, titleVisibility: .visible) {
            Button("End night and delete data", role: .destructive) { store.endNight() }
        } message: { Text("Every band forgets the group key and this phone deletes tonight's locations and alerts.") }
    }
}

struct SOSView: View {
    @EnvironmentObject var store: GroupStore
    @Environment(\.dismiss) private var dismiss
    let friend: Friend
    @State private var pulse = false
    @State private var navigate = false

    var body: some View {
        NavigationStack {
            VStack(spacing: 18) {
                Spacer()
                Circle().stroke(Color.red, lineWidth: 3).frame(width: 130, height: 130)
                    .overlay(Text(String(friend.name.prefix(1))).font(.system(size: 44, weight: .bold)))
                    .scaleEffect(pulse ? 1.08 : 1).animation(.easeInOut(duration: 0.7).repeatForever(), value: pulse)
                Text("\(friend.status == .sos ? "SOS" : "Help") · \(friend.name)").font(.largeTitle.bold())
                Text("\(Int(friend.distance)) m \(store.compassLetter(store.bearing(to: friend))) of you")
                    .foregroundStyle(.secondary)
                Spacer()
                Button { navigate = true } label: { Text("Walk me there").frame(maxWidth: .infinity) }
                    .buttonStyle(.borderedProminent).controlSize(.large)
                Text(friend.phoneAlive ? "Their phone is on: call them." : "Their phone is dead. For an emergency call 911.")
                    .font(.footnote).foregroundStyle(.secondary)
                Button("Dismiss · keep alert open") { dismiss() }
            }
            .padding(24)
            .background(RadialGradient(colors: [Color(hex: 0x5A1220), Color(hex: 0x1A070C)], center: .top, startRadius: 0, endRadius: 600).ignoresSafeArea())
            .navigationDestination(isPresented: $navigate) { NavigateView(friendID: friend.id) }
            .onAppear { pulse = true }
        }
    }
}
