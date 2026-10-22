import SwiftUI
import MessageUI

/// "Getting home" list for the group, shown on the Group tab.
struct GettingHomeSection: View {
    @EnvironmentObject var store: GroupStore
    var body: some View {
        let homeCount = store.friends.filter { $0.homeAt != nil }.count + (store.meHomeAt == nil ? 0 : 1)
        Section("Getting home · \(homeCount) of \(store.friends.count + 1) home") {
            row("You", store.meHomeAt)
            ForEach(store.friends) { f in row(f.name, f.homeAt) }
            Button { store.imHome() } label: { Label("I'm home", systemImage: "house.fill") }
        }
    }
    private func row(_ name: String, _ at: Date?) -> some View {
        HStack {
            Text(name)
            Spacer()
            Text(at.map { "home · " + $0.formatted(date: .omitted, time: .shortened) } ?? "out")
                .font(.caption.monospaced()).foregroundStyle(at == nil ? Color.secondary : Color.green)
        }
    }
}

/// Settings for who gets the "I'm home" text.
struct HomeTextSettings: View {
    @EnvironmentObject var store: GroupStore
    @State private var newName = ""
    @State private var newPhone = ""
    var body: some View {
        Section {
            TextField("Your name", text: $store.myName).onSubmit(store.saveHomeSettings)
            TextField("Message", text: $store.homeMessage, axis: .vertical).onSubmit(store.saveHomeSettings)
            ForEach(store.homeContacts) { c in LabeledContent(c.name, value: c.phone) }
                .onDelete { store.homeContacts.remove(atOffsets: $0); store.saveHomeSettings() }
            HStack {
                TextField("Name", text: $newName)
                TextField("Phone", text: $newPhone).keyboardType(.phonePad)
                Button("Add") {
                    guard !newName.isEmpty, !newPhone.isEmpty else { return }
                    store.homeContacts.append(HomeContact(name: newName, phone: newPhone)); newName = ""; newPhone = ""; store.saveHomeSettings()
                }
            }
        } header: { Text("Text when I'm home") } footer: {
            Text("Triple-press Button 1 when you get in. Friends in range hear it from your band; these people get a text from this phone. {name} and {time} fill in automatically.")
        }
    }
}

/// Wraps the system Messages composer so the text is sent by the user from their own number.
struct MessageComposer: UIViewControllerRepresentable {
    let recipients: [String]
    let body: String
    var onFinish: () -> Void
    func makeCoordinator() -> Coordinator { Coordinator(onFinish: onFinish) }
    func makeUIViewController(context: Context) -> MFMessageComposeViewController {
        let vc = MFMessageComposeViewController()
        vc.recipients = recipients; vc.body = body; vc.messageComposeDelegate = context.coordinator
        return vc
    }
    func updateUIViewController(_ vc: MFMessageComposeViewController, context: Context) {}
    final class Coordinator: NSObject, MFMessageComposeViewControllerDelegate {
        let onFinish: () -> Void
        init(onFinish: @escaping () -> Void) { self.onFinish = onFinish }
        func messageComposeViewController(_ controller: MFMessageComposeViewController, didFinishWith result: MessageComposeResult) { controller.dismiss(animated: true); onFinish() }
    }
}
