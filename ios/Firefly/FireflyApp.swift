import SwiftUI
import MessageUI

@main
struct FireflyApp: App {
    @StateObject private var store = GroupStore()

    var body: some Scene {
        WindowGroup {
            RootView()
                .environmentObject(store)
                .preferredColorScheme(.dark)
                .tint(.amber)
                .onAppear { store.requestPermissions() }
        }
    }
}

struct RootView: View {
    @EnvironmentObject var store: GroupStore
    @State private var tab = 0

    var body: some View {
        TabView(selection: $tab) {
            NavigationStack { GroupView() }.tabItem { Label("Group", systemImage: "person.3") }.tag(0)
            NavigationStack { GroupMapView() }.tabItem { Label("Map", systemImage: "map") }.tag(1)
            NavigationStack { AlertsView() }.tabItem { Label("Alerts", systemImage: "bell") }.tag(2)
                .badge(store.events.filter { $0.kind == .sos || $0.kind == .help }.count)
            NavigationStack { BandView() }.tabItem { Label("My band", systemImage: "capsule") }.tag(3)
            NavigationStack { PrivacyView() }.tabItem { Label("Privacy", systemImage: "lock.shield") }.tag(4)
        }
        .fullScreenCover(item: $store.activeAlert) { f in SOSView(friend: f) }
        .sheet(isPresented: $store.pendingHomeText) {
            if MFMessageComposeViewController.canSendText(), !store.homeContacts.isEmpty {
                MessageComposer(recipients: store.homeContacts.map(\.phone), body: store.homeTextBody) { store.pendingHomeText = false }
            } else {
                VStack(spacing: 12) {
                    Text("Add people under My band → Text when I'm home, and Firefly will text them next time.").multilineTextAlignment(.center)
                    Button("OK") { store.pendingHomeText = false }.buttonStyle(.borderedProminent)
                }.padding().presentationDetents([.medium])
            }
        }
    }
}

extension Color {
    static let amber = Color(hex: 0xF5B544)
    static let night = Color(hex: 0x0E0D16)
    static let panel = Color(hex: 0x17161F)
    init(hex: UInt32) { self.init(red: Double((hex >> 16) & 0xFF) / 255, green: Double((hex >> 8) & 0xFF) / 255, blue: Double(hex & 0xFF) / 255) }
}

extension Friend.Status {
    var color: Color {
        switch self { case .ok: .green; case .comeFindMe: .blue; case .help, .sos: .red; case .outOfRange: .orange }
    }
}
