<!-- Text of the Google Doc "Build plan" as of 2026-10-28T01:44:06Z (Tab 1 then Tab 2) -->

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

Yes! **Adding a feature that notifies the group when a friend leaves a certain radius is technically feasible.** I actually think this would be one of the most useful features for your nightlife safety wearable because it helps prevent friends from getting separated without realizing it.

However, the notification system would need to account for people temporarily leaving the group to use the bathroom, get drinks, or talk to someone.

## **Updated Wearable Features**

I recommend keeping **two buttons, one LED indicator, and one vibration motor**.

| **Feature** | **How it works** | **Technology** |
| :-: | :-: | :-: |
| **1. Find Friends** | Press Button 1 once. LED lights blink faster as you get closer to a friend. | UWB |
| **2. Come Find Me** | Press Button 1 twice. Connected friends receive a notification and two vibrations. | Bluetooth |
| **3. I’m Home** | Press Button 2 once. Sends an “I’m Home” notification to your group through the app. | Bluetooth + app/internet |
| **4. Separation Alert** ⭐ | Automatically notifies the group when a friend moves outside a selected distance. | UWB + Bluetooth |
| **5. Companion App** | Creates groups, displays available check-ins, and manages separation alerts. | Smartphone app |

I’ve removed the vibration that occurs when you find your friend. **Friend-finding will now use LED lights only.**

-----

## **How would the separation alert work?**

### **Example: Five friends at a nightclub**

Before going out, everyone connects their bracelets through the app.

The group selects a separation threshold.

For example:

  - **10 meters:** Small group staying close together.
  - **20 meters:** Friends moving around the same bar or club.
  - **30 meters:** Larger venue where friends have more freedom to move.

These are proposed settings, not guaranteed reliable detection distances.

### **Scenario**

You’re dancing with four friends.

One friend walks away to another section of the club.

When their bracelet detects that the distance has exceeded the selected threshold, the system starts a timer.

If they’re still outside the radius after two minutes, an alert is triggered.

**Example app notification:**

🔔 **Separation Alert**

“Emma may have moved more than 20 meters away from your group.”

The app could then offer a **Find Emma** option.

### **What if someone just goes to the bathroom?**

To prevent constant notifications, I recommend including:

**1. Adjustable radius:** Users select their preferred distance threshold.

**2. Alert delay:** The system waits 1–3 minutes before triggering a notification.

**3. Temporary pause:** Users can pause separation alerts when they intentionally leave the group.

**4. Individual settings:** Each person can decide whether to share separation alerts.

This is important because your product should promote safety without making people feel constantly monitored.

-----

## **Is this actually feasible?**

**Yes, but there is an important technical limitation.**

UWB can measure the distance between connected bracelets, so it can support radius-based alerts.

However, there are two different situations.

### **Situation A: Friend moves beyond your selected radius but remains connected**

✅ **Feasible.**

For example, the threshold is 10 meters, and your friend moves 15 meters away.

If the bracelets can still exchange UWB measurements, the system can detect that the distance exceeded the threshold.

A connected phone could then display an app notification.

### **Situation B: Friend moves completely out of wireless range**

⚠️ **More complicated.**

If their bracelet loses connection, your system won’t know their exact location.

It can only detect that their signal disappeared.

Instead of saying:

❌ “Emma is 50 meters away.”

Your app should say:

✅ “Connection with Emma lost. Last detected nearby 2 minutes ago.”

This distinction matters because the friend might have moved away, entered another room, or simply experienced interference.

### **What if someone’s phone dies?**

The bracelet can still detect separation or lost connections when communication is available.

However, **a dead phone cannot receive app notifications**.

For your product, I recommend:

  - **Working phone:** Receives the separation alert through the app.
  - **Dead phone:** The bracelet can provide an LED warning or vibration when it detects a separation event.
  - **Out-of-range friend:** Other connected devices can report the lost connection, but cannot confirm the friend’s current distance.

-----

## **How would the app look?**

Your app could have a **Group Safety Dashboard**.

### **Saturday Night — Group of 5**

| **Friend** | **Status** |
| :-: | :-: |
| Emma | 🟢 Nearby |
| Sarah | 🟢 Nearby |
| Olivia | 🟡 Outside selected radius |
| Chloe | ⚪ Connection lost |
| Mia | 🏠 I’m Home |

Users could select a separation-alert radius when creating the group.

The app would also allow them to adjust the delay before an alert is sent.

-----

## **Updated Product Design**

**Hardware:**

  - Two buttons
  - UWB chip for proximity measurement
  - Bluetooth chip for communication
  - Small LED indicator for friend-finding
  - Vibration motor for incoming alerts
  - Rechargeable battery

**Five core functions:**

1.  Find Friends
2.  Come Find Me
3.  I’m Home
4.  Automatic Separation Alerts
5.  Companion App

### **My recommendation**

**I would definitely include separation alerts in your startup concept.** They make the wearable more proactive instead of requiring someone to realize they’ve lost their friends before using the device.

For the first prototype, I would prioritize a simple separation alert between two bracelets. You could demonstrate that when one device moves beyond a threshold, the connected phone receives a notification.

One design decision is especially important: **Should your separation radius be measured from one designated friend (your buddy) or from the entire group?**

I recommend starting with a **designated buddy**, because measuring distance from one person is much simpler and more reliable than determining when someone has left an entire moving group.
