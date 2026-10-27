<!-- Text of the Google Doc "Build plan" as of 2026-10-27T20:44:27Z (Tab 1 then Tab 2) -->

Class 10/13

Ask claude to create and code watch/ wearable mockup describing  detailed parts. Make every part modeled to its real size.

Have app that connects to wearable for responsible friend. 

Understand privacy, location tracking, parts needed for wearable, price for each, where to buy.

Show what parts to order from Amazon,Show simulation, Renders, Drawings to scale, Show 3d model

Responsible friend has charge on phone so the app if for that friend.

Non responsible friend with no battery has wearable that doesn’t rely on phone battery

Create signup with waitlist to show the need and 

Send to reggie

**Different issues we face when going out:**

Phone dying, not signal in packed bars/clubs, friends splitting up when going home as some take ubers together or others stay at bar

**Requirements of wearable:**

Lightweight (less than 30g) , fashionable (looks like jewelry not a tracker)

**Proposed Solution**

We envision a compact, fashionable wearable, potentially in the form of a bracelet or jewelry, that allows friends to stay connected independently of their smartphones.

Our proposed features include:

  - Phone-independent connectivity: Essential functions continue working even when a user’s phone dies.
  - Friend-finding: Helps users locate friends within a connected group.
  - Discreet safety alerts: Allows users to signal friends when they need assistance.
  - Group check-ins: Enables friends to communicate their safety status throughout the night.
  - Fashionable and durable design: Lightweight, water-resistant, comfortable, and aesthetically appealing for nightlife settings.

**Proposed Wearable Features**

We envision a bracelet with two physical buttons, designed to be simple enough to operate in dark, loud, and crowded environments.

**Button 1: Friend-Finding & Communication**

  - **Single press:** Activate friend-finding mode to locate nearby connected friends through vibration or LED indicators.
  - **Double press:** Send a “Come find me” notification to connected friends.
  - **Long press:** Send an “I’m okay” check-in to the group.

**Button 2: Safety & Emergency**

  - **Single press:** Send a discreet “I need help” alert to designated friends.
  - **Double press:** Cancel an accidental alert.
  - **Long press (3 seconds):** Activate an urgent SOS alert to connected friends.

**Key issues and challenges during a night out** 

1.  Phones run low on battery after a night of taking pictures, using google maps, sharing locations, and communicating with friends 
2.  Large crowds, loud music, and dim lighting make it hard to find friends at festivals, clubs, or bars
      
    1.  GPS tracking might be inaccurate in basements or indoors 
    2.  In a crowded setting, it's hard to locate someone even with their location 
3.  Messaging is ineffective when people are distracted or have poor reception (even text messages) 
4.  Groups separate throughout the night to purchase drinks, use restrooms, or leave 
      
    1.  People get left behind and its hard to determine if everyone is safe 
    2.  Groups rely on one person to coordinate everyone’s locations 

**Key requirements for the wearable device** 

1.  Battery life (12-24 hours) 
2.  Must perform essential safety and communication functions without requiring an active smartphone connection 
      
    1.  Allow users to locate or communicate with connected friends even when their phones run out of battery 
3.  Must withstand crowded environments, accidental impacts, and be resistant to spilled drinks, rain, and water exposure
4.  Stylish, minimalist design that complements nightlife outfits 
5.  No bulky screens; should be lightweight, compact, and comfortable 
6.  Must help users locate connected friends within supported operating ranges 
7.  Provide intuitive guidance through vibrations or directional indicators 
8.  Distinguish between ordinary requests to reconnect and urgent safety alerts 
9.  Support subtle activation through a physical button, touch gesture, or simple interaction 
10. Minimal interaction (one or two simple actions) 
11. Privacy 
12. Affordable 

Questions to ask Claude:

How long is battery, weight of bracelet, what signal or network does it use, how much does it cost

Edits: text to send when home to, change design to look more like jewelry, 

You are my technical co-founder and industrial design lead. We are building a 

wearable startup product. Be technically honest: if something is unrealistic 

(weight, battery, range, cost, regulation), say so and propose an alternative 

instead of making it sound feasible. Use web search to verify current part 

prices, availability, and competitor details.

# PRODUCT

A jewelry-style bracelet that helps a friend group on a night out make sure 

NOBODY GETS LEFT BEHIND. It works without phones, because phones die, cell 

service fails in packed bars and clubs, GPS is inaccurate indoors, and groups 

split up (Ubers, restrooms, bar, going home).

Positioning: this is group accountability, not surveillance. Privacy and 

consent are central to the design.

Users:

\- "Organizer" (responsible friend): has a charged phone and the companion app. 

  Creates the group, pairs the bracelets, and sees everyone's status.

\- "Wearer": wears only the bracelet. All core features work with no phone.

Target market: college-age nightlife. We sell group packs (e.g. 4-packs) to 

the organizer. No subscription.

# COMPETITORS (research and compare; do not copy)

Totem (off-grid mesh friend finder, festivals), Lynq, Crowd Compass, 

invisaWear, Cuff, She's Birdie. Make a comparison table (price, features, 

subscription, range, battery, design). Tell me where we differentiate and 

where we're weaker. We are NOT a festival product; we are a city 

bar/club/house-party product.

# CORE FEATURES (v1)

Active:

\- Button 1: single press = friend-finding (LED/haptic guidance to a chosen 

  friend); double press = "Come find me"; long press = "I'm okay" check-in.

\- Button 2: single press = discreet "I need help" to the group; double press = 

  cancel; 3-second hold = urgent SOS. Add a 5-10 second haptic grace window 

  before any alert transmits so cancel is usable. Give each message type a 

  distinct vibration pattern. Propose a simpler button scheme if you think 

  this one is too complex for dark, loud, drunk use, and justify it.

Passive (new, key differentiators):

1\. Home-safe roll call: each wearer confirms they're home or in a ride; the 

   organizer app shows who hasn't confirmed and nudges the group after a 

   configurable time.

2\. Separation alert: if a wearer is out of the group's range or distance for 

   longer than a set time, buzz them and notify the group.

3\. Last-known location: when a bracelet dies or goes silent, the group sees 

   where and when it last reported.

4\. Stillness alert: the accelerometer detects no motion for several minutes 

   and prompts the wearer to confirm they're okay; no response alerts the group.

5\. Unacknowledged-alert escalation: if no friend acknowledges an SOS within 

   ~60 seconds, the organizer's app escalates to a backup contact. Do NOT 

   promise 911 integration; flag the legal issues instead.

6\. Tap-to-pair: pair bracelets by touching them together, with the app 

   handling group setup and keys.

Out of scope for v1: UWB, voice recording, video, cloud location storage.

# NETWORK ARCHITECTURE (design and justify)

Proposed: LoRa (915 MHz US ISM) for device-to-device messaging and position 

sharing; BLE for phone pairing and close-range proximity; on-board GNSS; 

magnetometer for bearing. Design:

1\. Mesh/relay with hop limit and duplicate suppression; compare flood routing 

   vs simple broadcast for groups of 2-10.

2\. Compact packet format: group ID, device ID, message type, sequence number, 

   timestamp, lat/long, battery, auth tag. Types: FIND, COME_FIND_ME, IM_OK, 

   HELP, CANCEL, SOS, POSITION_BEACON, HOME_SAFE, SEPARATION, STILLNESS.

3\. Timing: time-slotted beacons every 30-60 s; SOS has priority and repeats 

   until acknowledged.

4\. Acknowledgments so a sender knows an alert was received.

5\. Group provisioning over BLE before the night; no phone needed afterward.

6\. Direction guidance: GNSS + magnetometer bearing, with signal-strength 

   "hotter/colder" fallback indoors. Be honest about accuracy limits.

7\. Realistic range indoors in a crowded venue vs outdoors, including body 

   absorption and small-antenna effects.

8\. Regulatory: FCC Part 15, pre-certified modules, and EU 868 MHz limits for 

   later.

Tell me honestly how much of this works if only 2 of 4 bracelets are in range.

# HARD REQUIREMENTS

\- Under 30 g including strap

\- 12-24 h real-use battery

\- Water/spill/rain resistant (target IP67), shock resistant

\- No screen; buttons, LEDs, haptic motor only

\- Target BOM under $___ and retail under $___ per bracelet

\- Privacy-first (see below)

# AESTHETIC DESIGN (equal priority to the engineering)

It must look like jewelry people want to wear, not a tracker. Do real design 

work:

1\. Research current nightlife and Gen Z jewelry trends (cuffs, chain 

   bracelets, charm bracelets, beaded styles, minimalist bangles) and 

   summarize what's popular.

2\. Propose 3 distinct design concepts (e.g. slim cuff, charm bracelet with 

   the electronics in one charm, beaded/chain style). For each: form factor, 

   where each component lives, how the buttons are disguised, how the 

   LED/haptic feedback is hidden (e.g. light diffused through a gem or 

   engraved pattern), and an honest feasibility note on the antenna, battery, 

   and weight.

3\. Materials and finishes: gold, silver, rose gold, black, and a colorway 

   line. Compare PVD coating, plated brass, stainless steel, and silicone-

   wrapped options for durability, skin safety (nickel-free), and cost.

4\. Interchangeable strap/charm system so users can match outfits and we can 

   sell accessories.

5\. Comfort: sizing options, skin-contact materials, and an ergonomics check 

   that the wearer can find and press the buttons by feel in the dark.

6\. A design-language statement: name two or three brand directions (name, 

   mood, color palette, typography).

Recommend one concept and explain why.

# PRIVACY AND SAFETY

\- Location is shared only within an opted-in group; none is stored in the 

  cloud; sessions auto-expire at the end of the night.

\- Packets are encrypted with a group key and authenticated against spoofing.

\- Every member consents; a "pause sharing" option exists.

\- Address: stalking/misuse, rogue devices, data retention, minors, false-

  alarm fatigue, and liability for missed alerts. Give mitigations for each.

\- Marketing must not claim to prevent harm or replace 911. Note you are not 

  a lawyer and list what a lawyer should review.

# WORK IN PHASES (stop after each and wait for my approval)

Phase 1 - Feasibility: answer my questions below, competitor table, power 

budget (150/200/250 mAh cells), weight budget table, and a go/no-go view.

Phase 2 - Hardware: prototype BOM (e.g. Seeed XIAO nRF52840 + Wio-SX1262 

dev boards) and production-intent BOM. For each part: function, dimensions 

(mm), weight (g), price, alternatives, where to buy (Amazon where possible, 

else Digi-Key/Mouser/Adafruit/SparkFun/Seeed), and part numbers. Costs at 1, 

100, and 1,000 units.

Phase 3 - Design: the 3 aesthetic concepts above, then the chosen concept 

refined.

Phase 4 - Visuals: a system/network diagram; an interactive venue simulation 

(moving friends, relays, range circles, a crowd/indoor signal-loss toggle); 

true-scale dimensioned drawings with every part at real size; an interactive 

3D model with exploded view and labeled parts; renders in multiple finishes.

Phase 5 - Software and launch: companion app prototype for the organizer 

(group creation, tap-to-pair flow, live map, alert feed, per-friend 

battery/status, roll-call view); a landing page with a waitlist (name, email, 

how often they go out, biggest problem on nights out, what they'd pay); and a 

one-page summary for Reggie.

# FIRST, ANSWER THESE

1\. How long will the battery last, and what will it weigh?

2\. What network does it use and why?

3\. What's the realistic range in a packed club?

4\. Which passive features are hardest to build, and which matter most?

5\. Is the aesthetic goal compatible with the weight, antenna, and battery 

   limits? Where do we have to compromise?

Where something can't be done in this chat (ordering parts, physical testing, 

legal review), tell me what to do myself instead.

Last build plan edits:

Update to im safe to also add a im home button.

Update lora radio to a longer gps system for nyc to have range for miles

Waitlist and website wont open 

# Tab 2

# **2. Can you use their technology and improve the product?**

**Yes. You can build your own device using similar technologies.**

GPS, Bluetooth, UWB, and various radio communication technologies are not exclusive to Totem or Crowd Compass.

However, you cannot simply copy their proprietary software, patented inventions, or protected designs.

You would need to develop or license your own implementation.

The more important question is:

**What problems do existing festival wearables fail to solve for people going to clubs and bars?**

I see four promising opportunities.

## **Improvement 1: Accurate indoor friend-finding ⭐**

This should be your biggest potential differentiator.

**Existing product problem:**

Totem and Crowd Compass rely on satellite positioning to determine location.

But your target customers spend most of their time indoors.

**Your improvement:**

Use **Ultra-Wideband (UWB)** to measure the distance between nearby bracelets.

For example:

You’re at a nightclub, and your phone dies.

You press your bracelet.

Your bracelet detects another connected bracelet approximately five meters away.

As you approach your friend, your bracelet provides feedback.

UWB can enable accurate indoor distance measurement, although reliable directional tracking may require multiple antennas or additional positioning infrastructure.

**Why this matters:** Your product would be optimized for indoor nightlife rather than outdoor festivals.

-----

## **Improvement 2: A more advanced safety check-in system**

Existing festival wearables already offer SOS alerts, so an SOS button alone isn’t innovative.

Your opportunity is building a more complete check-in system.

### **Proposed buttons**

I would recommend **two physical buttons**.

|  |  |
| :- | :- |
| **Action** | **Function** |
| Button 1: Single press | Find nearby friends |
| Button 1: Double press | Send a “Come find me” request |
| Button 2: Single press | Send an “I’m safe” check-in |
| Button 2: Hold for 3 seconds | Send an urgent SOS alert |

The bracelet would use different vibration patterns to acknowledge requests.

Your app could display each friend’s last reported status.

For example:

🟢 Emma — Checked in

🟢 Sarah — Checked in

🟡 Olivia — Needs help finding friends

⚪ Chloe — Hasn’t responded

🔴 Mia — SOS activated

The important difference is that **you’re not only tracking someone’s location; you’re allowing them to communicate their safety status.**

However, alerts would only reach devices or apps connected through a functioning communication path.

-----

## **Improvement 3: Fashionable jewelry instead of festival equipment**

Look at Totem and Crowd Compass.

Their designs are focused on festivals and outdoor use.

Your target audience is different.

People going out to clubs may not want a relatively bulky electronic device hanging around their neck.

**Your improvement:**

Create a wearable that looks like:

  - A minimalist silver bracelet
  - A gold cuff
  - A fashionable wristband
  - A small jewelry charm

This could be especially attractive to young adults who want a safety device that complements their outfits.

Your competitive advantage would combine **fashion, convenience, and safety**, rather than focusing solely on tracking.

-----

## **Improvement 4: A dedicated nightlife app**

Instead of just offering location tracking, your app could help groups organize their entire night.

**Before going out:**

  - Create a private friend group.
  - Connect everyone’s bracelets.
  - Select a designated buddy.
  - Establish a meeting point.

**During the night:**

  - See available location information.
  - Receive check-ins and assistance requests.
  - Identify friends who haven’t responded.

**After going out:**

  - Confirm when friends arrive home.
  - Close the temporary safety group.
  - Automatically stop sharing locations.

An important detail: automatic arrival confirmation would require an available location source, such as a working phone or compatible home receiver.

|  |  |  |
| :- | :- | :- |
| **Technology** | **Function** | **Priority** |
| **Bluetooth Low Energy** | Connect bracelet to app and exchange nearby messages | Essential |
| **UWB** | More accurate indoor proximity detection | Essential for advanced friend-finding |
| **LoRa** | Longer-distance communication without cellular service | Optional |
| **GPS** | Outdoor tracking | Optional |
| **Vibration motor** | Discreet alerts and proximity feedback | Essential |

### **Why not simply copy Totem’s GPS + mesh technology?**

Because that would leave your product with the same major weakness: indoor positioning.

Instead, your startup could combine accurate short-range indoor detection with a separate radio communication system.

The tradeoff is that adding UWB, LoRa, and GPS increases cost, size, power consumption, and design complexity.

For a student startup prototype, **Bluetooth + UWB would be a reasonable starting point**. You could add long-range radio later if customer testing shows it’s necessary.

|  |  |  |  |
| :- | :- | :- | :- |
| **eature** | **Totem Compass** | **Crowd Compass** | **Your proposed wearable** |
| Phone-independent functionality | ✅ | ✅ | ✅ Target |
| Outdoor friend-finding | ✅ | ✅ | Optional |
| Indoor friend-finding | Limited | Limited | ⭐ Primary focus |
| SOS alerts | ✅ | Messaging available | ✅ Proposed |
| Safety check-ins | Limited | Preset messaging | ⭐ Dedicated system |
| Digital buddy system | Not a core feature | Not a core feature | ⭐ Proposed |
| Jewelry-inspired design | Festival accessory | Festival device | ⭐ Primary focus |
| Nightlife-specific app | No | No | ⭐ Proposed |
