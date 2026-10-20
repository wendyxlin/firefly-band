import SwiftUI
import MapKit

/// Everyone on a map. The phone's GPS is the anchor; friends are placed from their band's signal relative to it.
struct GroupMapView: View {
    @EnvironmentObject var store: GroupStore
    @State private var position: MapCameraPosition = .userLocation(fallback: .automatic)

    var body: some View {
        Map(position: $position) {
            UserAnnotation()
            ForEach(store.friends) { f in
                Annotation(f.name, coordinate: f.coordinate) {
                    NavigationLink(value: f.id) {
                        ZStack {
                            if f.distance > 25 { Circle().fill(Color(hex: f.colorHex).opacity(0.15)).frame(width: 60, height: 60) }
                            Circle().fill(Color(hex: f.colorHex)).frame(width: 26, height: 26)
                                .overlay(Text(String(f.name.prefix(1))).font(.caption.bold()).foregroundStyle(.black))
                                .overlay(Circle().stroke(f.status == .sos || f.status == .help ? .red : .clear, lineWidth: 3).padding(-4))
                        }
                    }
                }
            }
            MapCircle(center: store.myLocation, radius: 25).foregroundStyle(.green.opacity(0.08)).stroke(.green.opacity(0.5), lineWidth: 1)
        }
        .mapStyle(.standard(elevation: .flat, pointsOfInterest: .including([.nightlife, .restaurant, .publicTransport])))
        .mapControls { MapUserLocationButton(); MapCompass(); MapScaleView() }
        .navigationTitle("Everyone")
        .navigationBarTitleDisplayMode(.inline)
        .navigationDestination(for: UInt8.self) { id in NavigateView(friendID: id) }
        .safeAreaInset(edge: .bottom) {
            Text("Tap a friend for directions. Close friends are precise; far ones are an estimate.")
                .font(.footnote).foregroundStyle(.secondary).padding(10)
                .frame(maxWidth: .infinity).background(.ultraThinMaterial)
        }
    }
}

/// Turn-by-turn style guidance to one friend: compass arrow that follows the phone's heading,
/// distance, signal bars, steps, and a ping.
struct NavigateView: View {
    @EnvironmentObject var store: GroupStore
    let friendID: UInt8

    var body: some View {
        if let f = store.friends.first(where: { $0.id == friendID }) {
            let bearing = store.bearing(to: f)
            ScrollView {
                VStack(spacing: 16) {
                    HStack(spacing: 20) {
                        ZStack {
                            Circle().stroke(Color.secondary.opacity(0.3), lineWidth: 2)
                            Image(systemName: "location.north.fill")
                                .font(.system(size: 56))
                                .foregroundStyle(Color(hex: f.colorHex))
                                .rotationEffect(.degrees(bearing - store.heading)) // points at the friend as you turn
                                .animation(.easeOut(duration: 0.3), value: store.heading)
                        }
                        .frame(width: 120, height: 120)
                        VStack(alignment: .leading, spacing: 6) {
                            Text(f.distance < 3 ? "Here" : "\(Int(f.distance)) m").font(.system(size: 44, weight: .bold, design: .rounded))
                            Text("\(store.compassLetter(bearing)) · \(f.link)").font(.callout.monospaced()).foregroundStyle(.secondary)
                            SignalBars(level: f.bars)
                        }
                        Spacer()
                    }
                    .padding().background(Color.panel, in: RoundedRectangle(cornerRadius: 20))

                    Map(initialPosition: .automatic) {
                        UserAnnotation()
                        Marker(f.name, coordinate: f.coordinate).tint(Color(hex: f.colorHex))
                        MapPolyline(coordinates: [store.myLocation, f.coordinate]).stroke(Color(hex: f.colorHex), style: StrokeStyle(lineWidth: 4, dash: [2, 8]))
                    }
                    .frame(height: 200).clipShape(RoundedRectangle(cornerRadius: 16))

                    VStack(alignment: .leading, spacing: 10) {
                        Step(n: 1, text: f.distance < 3 ? "\(f.name) is right here. Look for the glowing band." : "Hold your phone flat and walk where the arrow points, about \(Int(f.distance)) m.")
                        Step(n: 2, text: f.distance < 25 ? "You're in Bluetooth range. Your own band pulses faster as you get closer." : "Too far for Bluetooth. The arrow sharpens within 25 m.")
                        Step(n: 3, text: "Ping their band so they stop and wait. It buzzes 3 times and lights up.")
                    }

                    HStack {
                        Button { store.ping(f) } label: { Label("Ping their band", systemImage: "dot.radiowaves.left.and.right").frame(maxWidth: .infinity) }
                            .buttonStyle(.borderedProminent)
                        if store.demoMode {
                            Button { store.simulateWalkToward(f) } label: { Label("Walk closer", systemImage: "figure.walk").frame(maxWidth: .infinity) }
                                .buttonStyle(.bordered)
                        }
                    }
                    if f.status == .sos || f.status == .help {
                        Button(role: .destructive) { store.resolve(f) } label: { Text("Found them · clear alert").frame(maxWidth: .infinity) }
                            .buttonStyle(.borderedProminent).tint(.red)
                    }
                }
                .padding()
            }
            .navigationTitle("Find \(f.name)")
        } else {
            ContentUnavailableView("Friend left the group", systemImage: "person.slash")
        }
    }
}

struct SignalBars: View {
    let level: Int
    var body: some View {
        HStack(alignment: .bottom, spacing: 3) {
            ForEach(0..<4) { i in
                RoundedRectangle(cornerRadius: 1).fill(i < level ? Color.amber : Color.secondary.opacity(0.3))
                    .frame(width: 5, height: CGFloat(6 + i * 4))
            }
        }
        .accessibilityLabel("\(level) of 4 bars")
    }
}

struct Step: View {
    let n: Int; let text: String
    var body: some View {
        HStack(alignment: .top, spacing: 10) {
            Text("\(n)").font(.caption.bold()).foregroundStyle(Color.amber)
                .frame(width: 22, height: 22).background(Color.panel, in: Circle())
            Text(text).font(.subheadline)
            Spacer(minLength: 0)
        }
        .padding(10).background(Color.panel, in: RoundedRectangle(cornerRadius: 12))
    }
}
