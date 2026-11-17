"""Build the Sprint 3 deck (revenue, go-to-market, unit economics) on the same template and helpers as Sprint 2.
Usage: python build_sprint3.py  -> out/Sprint3_Presentation_Firefly.pptx
Update DATA (and AD_SPEND once known) and re-run to refresh every number on the slides."""
import os, sys
SC = '/tmp/claude-0/-home-claude/05671788-1db4-51ad-86c7-0131427b2680/scratchpad'
src = open(SC + '/deck/build_deck.py').read().split('def build(key):')[0]
exec(src)
OUT = SC + '/s3deck/out'; os.makedirs(OUT, exist_ok=True)
IMG = SC + '/s3deck/img'; R = '/home/claude/firefly-band/v2-bracelet/renders'; IG = '/home/claude/firefly-band/marketing/instagram'
SITE = 'wearfirefly.github.io'

# ---------------- numbers (Google Form response sheet, [shop] rows, team test rows excluded) ----------------
DATA = dict(
    asof='Nov 12–17 (as of Nov 17, 4:25 PM)',
    price={129: (45, 0, 0), 169: (38, 1, 1), 199: (51, 2, 2)},            # price: (visitors, add to cart, checkout clicks)
    chan=[('Paid Instagram ads', 93, 0, 0), ('Instagram organic (bio link)', 30, 3, 3), ('Other (direct, Facebook, search)', 11, 0, 0)],
    waitlist=0)
AD_SPEND = None      # total dollars spent on the two paid ads; set it and re-run
PRICE, COGS, FEES, SHIP, RET = 169, 80, 5, 10, 8
MARGIN = PRICE - COGS - FEES - SHIP - RET                                 # 66
V = sum(v[0] for v in DATA['price'].values()); ATC = sum(v[1] for v in DATA['price'].values()); CO = sum(v[2] for v in DATA['price'].values())
pct = lambda a, b: (f'{100 * a / b:.1f}'.rstrip('0').rstrip('.') + '%') if b else '0%'
TODO = '[add]'

def dots(d, s, x, y, n, hot, per_row, pitch, size, base=BLUSH, hotcol=CORAL):
    """Icon array: n dots, the last `hot` ones highlighted. Returns the height used."""
    for i in range(n):
        d.circ(s, x + (i % per_row) * pitch, y + (i // per_row) * pitch, size, hotcol if i >= n - hot else base)
    return ((n - 1) // per_row + 1) * pitch

def card(d, s, x, y, w, h, head, col, lines, fill=WHITE):
    d.box(s, x, y, w, h, fill=fill, line=INK if fill == WHITE else None, radius=0.06)
    d.tb(s, x + 0.14, y + 0.08, w - 0.28, h - 0.14, '', lines=[(head, dict(size=9, bold=True, color=col))] + lines, spacing=3)

def build():
    c = dict(file='Sprint3_Presentation_Firefly', name='Firefly'); d = Deck(c)
    P = DATA['price']

    # 1 Introduction
    s = d.slide('TITLE_L', notes="0:00–0:15. “Firefly is a slim bracelet that finds your friends and tells them you’re home, even when your phones die. This sprint we tested two things: will students pay for it, and can we reach them at a cost that makes sense.”")
    d.tb(s, 0.75, 1.3, 5.0, 0.9, 'Firefly', size=54)
    d.tb(s, 0.75, 2.2, 4.7, 1.0, 'A slim bracelet that finds your friends and tells them you’re home, even when your phones die', size=16, color=GREY)
    d.tb(s, 0.75, 3.15, 4.7, 0.4, 'Sprint 3 · Will they pay, and can we reach them?', size=14, italic=True, color=CORAL)
    d.box(s, 0.75, 3.85, 4.4, 0.42, line=INK, radius=0.5); d.tb(s, 0.75, 3.85, 4.4, 0.42, TEAM, size=12, align='c', anchor='m')
    d.box(s, 5.75, 1.0, 3.6, 3.6, fill=PEACH, line=None, radius=0.06); d.pic(s, R + '/v2-hero.jpg', 5.9, 1.15, 3.3, 3.3, focus=(0.55, 0.45))

    # 2 Revenue assumptions
    s = d.slide('CONTENT', 'Revenue: What We Assumed', notes="0:15–0:45. How: a one-time purchase, no subscription, because the cellular data costs us about $10 for ten years so we can bundle it. How much: $169, with pack discounts because Firefly only works when friends wear one too. Who pays: the student, usually the ‘group parent’ from our Sprint 1 interviews. Why we believed it: (1) 12 interviews showed one friend chases everyone home; (2) competitors sit at $29–$99 but all need a working phone; (3) built up from cost, $169 leaves about $66 per bracelet; (4) value: it works with a dead phone and has no monthly fee.")
    for i, (hd, big, sub, col) in enumerate([('HOW WE CHARGE', 'One-time purchase', 'No subscription. Cellular data is included for life.', TEAL),
                                             ('HOW MUCH', '$169 per bracelet', 'Packs of 2, 4, 6 save 10%, 20%, 25%.', CORAL),
                                             ('WHO PAYS', 'The student', 'Often the “group parent” buying for friends.', GREEN)]):
        x = 0.75 + i * 2.88
        d.box(s, x, 1.3, 2.74, 1.38, fill=WHITE, line=INK, radius=0.06); d.box(s, x, 1.3, 2.74, 0.34, fill=col, line=INK, radius=0.25)
        d.tb(s, x + 0.14, 1.3, 2.4, 0.34, hd, size=10, bold=True, color=WHITE, anchor='m')
        d.tb(s, x + 0.14, 1.72, 2.5, 0.4, big, size=17, bold=True); d.tb(s, x + 0.14, 2.14, 2.5, 0.5, sub, size=10, color=GREY)
    d.tb(s, 0.75, 2.85, 8.5, 0.28, 'WHY WE BELIEVED IT', size=9, bold=True, color=CORAL)
    ev = [('Our interviews', '12 students: one friend texts everyone “u home?” until they answer.', TEAL),
          ('Competition', 'Safety charm $49–99, item tracker $29. All need a working phone.', ORANGE),
          ('Built up from cost', f'About ${COGS} to make. ${PRICE} leaves about ${MARGIN} after fees, shipping, returns.', CORAL),
          ('Value to the user', 'Works when the phone is dead. No monthly fee. Looks like jewelry.', GREEN)]
    for i, (h, body, col) in enumerate(ev):
        x = 0.75 + i * 2.158
        d.box(s, x, 3.15, 2.03, 1.62, fill=PEACH, line=None, radius=0.06); d.circ(s, x + 0.14, 3.27, 0.3, col, str(i + 1), 10)
        d.tb(s, x + 0.52, 3.25, 1.45, 0.34, h, size=11, bold=True, anchor='m'); d.tb(s, x + 0.14, 3.7, 1.78, 1.05, body, size=10.5, color=INK)

    # 3 Revenue test design
    s = d.slide('CONTENT', 'Revenue Test: A Real Shop With No Stock', notes="0:45–1:10. We ran an out-of-stock test, the high-intent test from the kickoff. The shop is live at wearfirefly.github.io. Each visitor is randomly shown one of three prices and keeps that price if they come back. They pick a colour and a pack and add to cart. At checkout we say it is out of stock, that nothing was charged, and offer the waitlist. We count a checkout click as the stand-in for a purchase. We set the pass bar before launch: at least 10% of visitors clicking checkout at $169.")
    steps = [('1', 'Taps our link', 'From Instagram. Every link is tagged, so we know the post or ad.', IMG + '/grid.jpg', (0.5, 0.0), CORAL),
             ('2', 'Sees 1 of 3 prices', '$129, $169 or $199, picked at random and kept on return visits.', IMG + '/buy-top.png', (0.0, 0.0), ORANGE),
             ('3', 'Adds to cart', 'Single, 2-pack, 4-pack or 6-pack, in four colours.', IMG + '/drawer-top.png', (0.5, 0.0), TEAL),
             ('4', 'Sees “Out of stock”', 'At checkout. Nothing is charged, and we offer the waitlist.', IMG + '/oos.png', (0.5, 0.0), GREEN)]
    cw, gap = 1.95, 0.233
    for i, (num, h, body, img, focus, col) in enumerate(steps):
        x = 0.75 + i * (cw + gap)
        d.box(s, x, 1.3, cw, 2.72, fill=WHITE, line=INK, radius=0.06)
        d.pic(s, img, x + 0.08, 1.38, cw - 0.16, 1.42, focus=focus, frame=True)
        d.circ(s, x - 0.1, 1.2, 0.32, col, num, 10)
        d.tb(s, x + 0.1, 2.86, cw - 0.2, 0.32, h, size=11.5, bold=True); d.tb(s, x + 0.1, 3.17, cw - 0.2, 0.8, body, size=9, color=GREY)
        if i < 3: d.box(s, x + cw + 0.03, 2.5, 0.17, 0.2, fill=INK, line=None, shape=MSO_SHAPE.RIGHT_ARROW)
    d.box(s, 0.75, 4.18, 4.15, 0.6, fill=PEACH, line=None, radius=0.1)
    d.tb(s, 0.9, 4.2, 3.9, 0.56, '', lines=[('WHAT WE MEASURE', dict(size=9, bold=True, color=CORAL)), ('Checkout clicks ÷ visitors, at each price', dict(size=11))], spacing=1)
    d.box(s, 5.1, 4.18, 4.15, 0.6, fill=WHITE, line=INK, radius=0.1)
    d.tb(s, 5.25, 4.2, 3.9, 0.56, '', lines=[('PASS BAR, SET BEFORE LAUNCH', dict(size=9, bold=True, color=TEAL)), ('At least 10% of visitors click checkout at $169', dict(size=11))], spacing=1)

    # 4 Revenue results
    s = d.slide('CONTENT', f'Revenue Test: {CO} of {V} Clicked Checkout', notes=f"1:10–1:45. Each dot is one real visitor; coral dots clicked checkout. {V} visitors in six days, {CO} checkout clicks: {pct(CO, V)}, well under our 10% bar. The surprise: nobody clicked at the cheapest price. All {CO} clicks were at $169 and $199, so price was not what stopped people. And none of the {CO} left an email for the waitlist. What we changed because of this: we removed the price question nobody answered, rebuilt the out-of-stock screen around the waitlist, and added a Show more section and session replays so we can see where people drop off. Data: {DATA['asof']}.")
    cw = 2.74
    for i, pr in enumerate([129, 169, 199]):
        v, a, co = P[pr]; x = 0.75 + i * 2.88
        d.box(s, x, 1.3, cw, 2.2, fill=WHITE, line=INK, radius=0.06)
        d.tb(s, x + 0.14, 1.35, 1.2, 0.42, f'${pr}', size=20, bold=True)
        d.tb(s, x + 1.25, 1.37, 1.38, 0.42, '', lines=[(f'{co} of {v}', dict(size=13, bold=True, color=CORAL if co else GREY)), ('clicked checkout', dict(size=8.5, color=GREY))], align='r', spacing=0)
        dots(d, s, x + 0.19, 1.93, v, co, 10, 0.24, 0.185)
    d.tb(s, 0.75, 3.52, 5.0, 0.25, 'Each dot = one visitor shown that price. Coral = clicked checkout.', size=8.5, color=GREY)
    d.tb(s, 5.6, 3.52, 3.65, 0.25, f'Shop data, {DATA["asof"]}', size=8.5, color=GREY, align='r')
    card(d, s, 0.75, 3.82, 4.15, 0.96, 'WHAT WE LEARNED', CORAL, [(f'{pct(CO, V)} clicked checkout. Our bar was 10%.', dict(size=10)), ('Price was not the blocker: 0 clicks at $129.', dict(size=10)), (f'{DATA["waitlist"]} of {CO} joined the waitlist afterwards.', dict(size=10))], fill=PEACH)
    card(d, s, 5.1, 3.82, 4.15, 0.96, 'WHAT WE CHANGED', TEAL, [('Removed the price question nobody answered.', dict(size=10)), ('Rebuilt “out of stock” around the waitlist.', dict(size=10)), ('Added “Show more” and session replays.', dict(size=10))])

    # 5 Revenue assessment
    s = d.slide('CONTENT', 'Revenue: How Sure Are We?', notes="1:45–2:10. Confidence is low to medium. We are confident most cold visitors will not buy at any of these prices. We are not confident about which price is best: three clicks cannot rank three prices, and a click is not a payment. Next we would test a $10 refundable deposit, which is real money; a parent as the payer; a payment plan; and a cheaper version without cellular. Verdict: the model is plausible but not proven. $169 keeps a healthy margin, but demand at that price is unproven.")
    cols = [('CONFIDENCE: LOW TO MEDIUM', ORANGE, [(f'Solid: {V} real visitors, random prices, set bar.', dict(size=11)), (f'Weak: {CO} clicks cannot rank three prices.', dict(size=11)), ('A click is not a payment.', dict(size=11))]),
            ('WHAT WE’D TEST NEXT', TEAL, [('A $10 refundable deposit (real money).', dict(size=11)), ('Parents as the payer, as a gift.', dict(size=11)), ('“4 payments of $42” next to $169.', dict(size=11)), ('A $99 version without cellular.', dict(size=11))]),
            ('IS THE MODEL STRONG?', CORAL, [('Plausible, not proven.', dict(size=13, bold=True)), (f'${PRICE} one-time leaves about ${MARGIN} a bracelet, and nobody needed the lowest price.', dict(size=11)), ('Demand at that price is still unproven.', dict(size=11))])]
    for i, (h, col, lines) in enumerate(cols):
        x = 0.75 + i * 2.88
        d.box(s, x, 1.3, 2.74, 2.55, fill=PEACH if i == 2 else WHITE, line=None if i == 2 else INK, radius=0.06)
        d.box(s, x, 1.3, 2.74, 0.34, fill=col, line=INK, radius=0.25); d.tb(s, x + 0.14, 1.3, 2.5, 0.34, h, size=9.5, bold=True, color=WHITE, anchor='m')
        d.tb(s, x + 0.16, 1.78, 2.44, 2.0, '', lines=lines, spacing=7)
    d.box(s, 0.75, 4.05, 8.5, 0.72, fill=INK, line=None, radius=0.2)
    d.tb(s, 1.0, 4.05, 8.0, 0.72, '', lines=[('NEXT SPRINT’S TEST', dict(size=9, bold=True, color=ORANGE)), ('A $10 refundable deposit to reserve a bracelet at $169', dict(size=13, bold=True, color=WHITE))], anchor='m', spacing=2)

    # 6 GTM assumptions
    s = d.slide('CONTENT', 'Go-to-Market: What We Assumed', notes="2:10–2:40. Channel: Instagram, because we can target by age and location, 18 to 24 within five miles of Washington Square, and our whole test group is that audience. Message: three hooks, one per ad: finding friends when your phone dies, saying you’re home without texting, and that it looks like jewelry. Incentive: pack discounts, because Firefly needs friends to wear one too. Why we believed it: a comparable safety brand, She’s Birdie, sells to students through campus pages and social. Our back-of-envelope math: 50 cents to a dollar per click, 10% clicking checkout, one in three of those buying, gives $15 to $30 to acquire a customer against about $66 of margin.")
    for i, (hd, big, sub, col) in enumerate([('CHANNEL', 'Instagram', 'Posts, reels and paid ads to ages 18–24 within 5 miles of Washington Square.', TEAL),
                                             ('MESSAGE', 'Three hooks', 'Phone dead? Still found. · “I’m home” without the text. · Looks like jewelry.', CORAL),
                                             ('INCENTIVE', 'Bring your group', 'Packs of 2, 4, 6 save 10–25%, because it works best when friends wear one.', GREEN)]):
        x = 0.75 + i * 2.88
        d.box(s, x, 1.3, 2.74, 1.5, fill=WHITE, line=INK, radius=0.06); d.box(s, x, 1.3, 2.74, 0.34, fill=col, line=INK, radius=0.25)
        d.tb(s, x + 0.14, 1.3, 2.4, 0.34, hd, size=10, bold=True, color=WHITE, anchor='m')
        d.tb(s, x + 0.14, 1.72, 2.5, 0.4, big, size=17, bold=True); d.tb(s, x + 0.14, 2.14, 2.5, 0.62, sub, size=9.5, color=GREY)
    card(d, s, 0.75, 2.98, 4.15, 1.78, 'WHY WE BELIEVED IT', CORAL, [('Instagram lets us target our exact tester profile: NYU-area students, 18–24.', dict(size=10)), ('She’s Birdie, a safety brand for the same audience, sells through campus pages and social.', dict(size=10)), ('$100 budget: enough for small paid tests.', dict(size=10))], fill=PEACH)
    d.box(s, 5.1, 2.98, 4.15, 1.78, fill=WHITE, line=INK, radius=0.06)
    d.tb(s, 5.24, 3.06, 3.9, 0.25, 'BACK-OF-ENVELOPE: COULD CAC BEAT LTV?', size=9, bold=True, color=TEAL)
    for k, (big, lab) in enumerate([('$0.50–1', 'per click'), ('10%', 'click checkout'), ('1 in 3', 'then buy')]):
        xx = 5.24 + k * 1.33; d.tb(s, xx, 3.36, 1.2, 0.36, big, size=15, bold=True); d.tb(s, xx, 3.7, 1.2, 0.25, lab, size=8.5, color=GREY)
        if k < 2: d.tb(s, xx + 1.02, 3.36, 0.3, 0.36, '÷', size=14, color=GREY, align='c')
    d.box(s, 5.24, 4.08, 3.87, 0.5, fill=PEACH, line=None, radius=0.3)
    d.tb(s, 5.24, 4.08, 3.87, 0.5, f'= $15–30 to win a customer, vs. about ${MARGIN} earned', size=10.5, bold=True, align='c', anchor='m')

    # 7 GTM test design
    s = d.slide('CONTENT', 'GTM Test: Instagram, Organic vs. Paid', notes="2:40–3:00. We built the Instagram page with posts and reels, and put the shop link in the bio. Then we ran two paid ads on November 16 and 17. Every link carries a tag, so the shop knows whether a visitor came from the bio, a paid ad, or somewhere else. We measured the same funnel as the revenue test, split by channel: visit, add to cart, checkout click.")
    d.box(s, 0.75, 1.3, 4.95, 0.32, fill=TEAL, line=None, radius=0.3); d.tb(s, 0.9, 1.3, 4.7, 0.32, 'ORGANIC · POSTS + REELS · LINK IN BIO', size=10, bold=True, color=WHITE, anchor='m')
    d.box(s, 5.9, 1.3, 3.35, 0.32, fill=ORANGE, line=None, radius=0.3); d.tb(s, 6.05, 1.3, 3.1, 0.32, 'PAID · 2 ADS · NOV 16–17', size=10, bold=True, color=WHITE, anchor='m')
    d.pic(s, IMG + '/grid.jpg', 0.75, 1.75, 2.1, 2.62, frame=True)
    for k, f in enumerate(['reels/reel1-u-home-cover.jpg', 'reels/reel2-three-reasons-cover.jpg']): d.pic(s, IG + '/' + f, 2.98 + k * 1.4, 1.75, 1.3, 2.31, frame=True)
    d.tb(s, 2.98, 4.08, 2.7, 0.3, 'Reels: 7–13 s, hook in the first second', size=8.5, color=GREY, align='c')
    for k, f in enumerate(['ad-A-finding.jpg', 'ad-C-jewelry.jpg']): d.pic(s, IG + '/' + f, 6.22 + k * 1.5, 1.75, 1.3, 2.31, frame=True)
    d.tb(s, 5.9, 4.08, 3.35, 0.3, 'Ad creative from our kit · ages 18–24 near NYU', size=8.5, color=GREY, align='c')
    d.box(s, 0.75, 4.42, 8.5, 0.38, fill=PEACH, line=None, radius=0.3)
    d.tb(s, 0.95, 4.42, 8.1, 0.38, 'Every link is tagged, so each visitor is counted by channel: visit → add to cart → checkout click', size=10.5, anchor='m', align='c')

    # 8 GTM results
    ch = DATA['chan']; paid, org, oth = ch
    spend_txt = f'${AD_SPEND:.0f} spent = ${AD_SPEND / paid[1]:.2f} per visit' if AD_SPEND else f'Ad spend: {TODO} = {TODO} per visit'
    s = d.slide('CONTENT', 'GTM Test: Ads Brought Traffic, Not Buyers', notes=f"3:00–3:35. Paid ads brought {paid[1]} of our {V} visitors, about {round(100 * paid[1] / V)}% of the traffic, and not one added to cart. Organic Instagram, people who came through the link in our bio, brought {org[1]} visitors and all {org[3]} checkout clicks: {pct(org[3], org[1])}, which is our original bar. So a cold audience scrolling past an ad does not buy a ${PRICE} bracelet on first sight, but people who already follow us do click. What we changed: we moved the shop to a clean link, wearfirefly, because the old one showed a personal GitHub name; we set up a live dashboard that splits every visit by ad and channel; and we are moving effort from cold ads to warm channels. " + ("" if AD_SPEND else "FILL IN the ad spend from Instagram before presenting."))
    geo = [(0.75, 3.7, 20), (4.65, 2.55, 13), (7.4, 1.85, 9)]
    for (name, v, a, co), (x, w, per) in zip(ch, geo):
        d.box(s, x, 1.3, w, 2.2, fill=WHITE, line=INK, radius=0.06)
        d.tb(s, x + 0.14, 1.36, w - 0.28, 0.3, name.upper() if len(name) < 22 else name.split(' (')[0].upper(), size=9, bold=True, color=ORANGE if name.startswith('Paid') else TEAL if name.startswith('Insta') else GREY)
        d.tb(s, x + 0.14, 1.62, w - 0.28, 0.4, '', lines=[(f'{co} of {v}', dict(size=17, bold=True, color=CORAL if co else INK)), (' clicked checkout' + (f'  ·  {pct(co, v)}' if co else ''), dict(size=9, color=GREY))], spacing=0)
        dots(d, s, x + 0.17, 2.42, v, co, per, 0.17, 0.125)
    d.tb(s, 0.75, 3.52, 5.2, 0.25, 'Each dot = one visitor. Coral = clicked checkout. ' + spend_txt, size=8.5, color=CORAL if not AD_SPEND else GREY)
    d.tb(s, 5.6, 3.52, 3.65, 0.25, f'Shop data, {DATA["asof"]}', size=8.5, color=GREY, align='r')
    card(d, s, 0.75, 3.82, 4.15, 0.96, 'WHAT WE LEARNED', CORAL, [(f'Paid: {round(100 * paid[1] / V)}% of visitors, 0 add-to-carts.', dict(size=10)), (f'Followers: {pct(org[3], org[1])} clicked checkout, our 10% bar.', dict(size=10)), ('Cold audiences do not buy at first sight.', dict(size=10))], fill=PEACH)
    card(d, s, 5.1, 3.82, 4.15, 0.96, 'WHAT WE CHANGED', TEAL, [(f'New link, {SITE}: no personal name.', dict(size=10)), ('Live dashboard splits every visit by ad and channel.', dict(size=10)), ('Shifting from cold ads to warm channels.', dict(size=10))])

    # 9 GTM assessment
    s = d.slide('CONTENT', 'Go-to-Market: How Sure Are We?', notes="3:35–4:00. We are fairly confident that cold paid ads do not convert yet: 93 visitors and zero carts. But it was two ads over two days, so we have not tested many messages. We are less confident in the organic number: 30 visitors is small, and some are probably friends of the team. Next we would test the warm channels we already tagged: group chats and flyers, a referral code for friend groups, a parent gift ad before the holidays, and showing ads again to people who already visited. Verdict: not a strong go-to-market yet. The channel that converts is small, and the channel that scales does not convert.")
    cols = [('CONFIDENCE: MEDIUM', ORANGE, [(f'Fairly sure: cold ads do not convert yet ({paid[1]} visits, 0 carts).', dict(size=11)), ('Less sure: only 2 ads over 2 days.', dict(size=11)), (f'Organic is {org[1]} visitors, and some may be friends.', dict(size=11))]),
            ('WHAT WE’D TEST NEXT', TEAL, [('Group chats and flyers (links already tagged).', dict(size=11)), ('A referral code for friend groups.', dict(size=11)), ('A parent gift ad before the holidays.', dict(size=11)), ('Ads shown again to past visitors.', dict(size=11))]),
            ('IS THE STRATEGY STRONG?', CORAL, [('Not yet.', dict(size=13, bold=True)), ('The channel that converts (our followers) is small.', dict(size=11)), ('The channel that scales (paid ads) does not convert.', dict(size=11))])]
    for i, (h, col, lines) in enumerate(cols):
        x = 0.75 + i * 2.88
        d.box(s, x, 1.3, 2.74, 2.55, fill=PEACH if i == 2 else WHITE, line=None if i == 2 else INK, radius=0.06)
        d.box(s, x, 1.3, 2.74, 0.34, fill=col, line=INK, radius=0.25); d.tb(s, x + 0.14, 1.3, 2.5, 0.34, h, size=9.5, bold=True, color=WHITE, anchor='m')
        d.tb(s, x + 0.16, 1.78, 2.44, 2.0, '', lines=lines, spacing=7)
    d.box(s, 0.75, 4.05, 8.5, 0.72, fill=INK, line=None, radius=0.2)
    d.tb(s, 1.0, 4.05, 8.0, 0.72, '', lines=[('NEXT SPRINT’S TEST', dict(size=9, bold=True, color=ORANGE)), ('Group chats, flyers and a referral code, each with its own tagged link', dict(size=13, bold=True, color=WHITE))], anchor='m', spacing=2)

    # 10 Unit economics
    s = d.slide('CONTENT', 'Unit Economics: Not Profitable Yet', notes=f"4:00–4:35. The product side works. At ${PRICE}, after about ${COGS} to make, ${FEES} in card fees, ${SHIP} shipping and ${RET} for returns, we keep about ${MARGIN} per bracelet. It is a one-time purchase, so that ${MARGIN} is the lifetime value. For a healthy three-to-one ratio we can spend at most ${MARGIN // 3} to win a customer. If one in three checkout clicks becomes a purchase, that means about ${MARGIN / 9:.0f} per checkout click. Our followers clicked for free, but paid ads produced no checkout clicks at all, so paid acquisition cost is not measurable yet. Conclusion: we would make money on each bracelet, but we have not shown we can buy customers for less than we earn. The math is in the appendix.")
    d.tb(s, 0.75, 1.28, 5.0, 0.26, 'WHAT ONE BRACELET EARNS (LTV)', size=9, bold=True, color=TEAL)
    items = [('Price', PRICE, INK), ('Make it', -COGS, GREY), ('Card fees', -FEES, GREY), ('Shipping', -SHIP, GREY), ('Returns', -RET, GREY), ('We keep', MARGIN, GREEN)]
    scale = 1.7 / PRICE; base = 3.42; run = 0; bw = 0.62
    for i, (lab, val, col) in enumerate(items):
        x = 0.8 + i * 0.83
        if i == 0 or i == len(items) - 1: top = base - abs(val) * scale; h = abs(val) * scale
        else: top = base - run * scale; h = abs(val) * scale
        if i == 0: run = val
        elif i < len(items) - 1: run += val
        d.box(s, x, top, bw, max(h, 0.04), fill=col if i in (0, len(items) - 1) else BLUSH, line=None, radius=0.04)
        d.tb(s, x - 0.1, top - 0.3, bw + 0.2, 0.28, (f'${val}' if val > 0 else f'−${-val}'), size=11, bold=True, align='c', color=GREEN if i == len(items) - 1 else INK)
        d.tb(s, x - 0.1, base + 0.04, bw + 0.2, 0.26, lab, size=8.5, color=GREY, align='c')
    d.box(s, 6.0, 1.3, 3.25, 2.4, fill=WHITE, line=INK, radius=0.06)
    d.tb(s, 6.14, 1.36, 3.0, 0.26, 'WHAT ONE CUSTOMER COSTS (CAC)', size=9, bold=True, color=ORANGE)
    rows = [('Target for 3 : 1', f'≤ ${MARGIN // 3}', INK), ('= per checkout click*', f'≤ ${MARGIN / 9:.0f}', INK), ('Followers (organic)', f'$0 · {org[3]} clicks', GREEN), ('Paid ads', f'{("$%.0f" % AD_SPEND) if AD_SPEND else TODO} · 0 clicks', RED)]
    for k, (lab, val, col) in enumerate(rows):
        y = 1.68 + k * 0.48
        d.tb(s, 6.14, y, 1.75, 0.4, lab, size=10, color=GREY, anchor='m'); d.tb(s, 7.75, y, 1.4, 0.4, val, size=12.5, bold=True, color=col, anchor='m', align='r')
    d.tb(s, 6.14, 3.42, 3.0, 0.24, '*if 1 in 3 checkout clicks becomes a purchase', size=7.5, color=GREY)
    d.box(s, 0.75, 3.92, 8.5, 0.85, fill=PEACH, line=None, radius=0.1)
    d.tb(s, 0.95, 3.96, 8.1, 0.78, '', lines=[('CONCLUSION', dict(size=9, bold=True, color=CORAL)), (f'Each bracelet earns about ${MARGIN}, so the product can be profitable. But paid ads won no buyers, so we have not shown CAC below LTV. Next: prove a warm channel under ${MARGIN // 3} per customer.', dict(size=11))], spacing=2)

    # 11 Learning and iteration
    s = d.slide('CONTENT', 'What We Learned, What We Changed', notes="4:35–5:00. Four times this sprint the data changed what we did. One: the bio link alone brought only 12 visitors in two days, too few to judge, so we turned on two paid ads to get past 100. Two: paid ads brought traffic and no carts, so we stopped treating paid as our main channel. Three: nobody answered the price question or joined the waitlist, so we removed the question and rebuilt the screen around the waitlist. Four: we could not see why people left, so we added session replays, a Show more section we can track, and a cleaner link. Next sprint: a deposit test and warm channels. Thank you.")
    steps = [('Nov 12–13', 'Bio link only', '12 visitors in 2 days. Too few to judge.', 'Turned on two paid ads to pass 100 visitors.', TEAL),
             ('Nov 16–17', 'Two paid ads', f'{paid[1]} visits, 0 carts.', 'Stopped leading with cold ads; next is warm channels.', ORANGE),
             ('Nov 17', 'Out-of-stock screen', '0 price answers, 0 waitlist emails.', 'Removed the question; screen is now waitlist only.', CORAL),
             ('Nov 17', 'Why do people leave?', 'We could not see it.', f'Session replays, tracked “Show more”, new link {SITE}.', GREEN)]
    cw, gap = 1.95, 0.233
    d.box(s, 0.9, 1.56, 8.2, 0.03, fill=INK, line=None, shape=MSO_SHAPE.RECTANGLE)
    for i, (when, what, saw, did, col) in enumerate(steps):
        x = 0.75 + i * (cw + gap)
        d.circ(s, x + cw / 2 - 0.16, 1.41, 0.32, col, str(i + 1), 10)
        d.tb(s, x, 1.8, cw, 0.25, when, size=9, bold=True, color=col, align='c'); d.tb(s, x, 2.04, cw, 0.3, what, size=11.5, bold=True, align='c')
        d.box(s, x, 2.42, cw, 0.72, fill=PEACH, line=None, radius=0.08)
        d.tb(s, x + 0.1, 2.46, cw - 0.2, 0.66, '', lines=[('WE SAW', dict(size=8, bold=True, color=CORAL)), (saw, dict(size=10.5))], spacing=2)
        d.box(s, x + cw / 2 - 0.1, 3.16, 0.2, 0.15, fill=INK, line=None, shape=MSO_SHAPE.DOWN_ARROW)
        d.box(s, x, 3.33, cw, 0.92, fill=WHITE, line=INK, radius=0.08)
        d.tb(s, x + 0.1, 3.37, cw - 0.2, 0.86, '', lines=[('WE CHANGED', dict(size=8, bold=True, color=TEAL)), (did, dict(size=10.5))], spacing=2)
    d.box(s, 0.75, 4.38, 8.5, 0.42, fill=INK, line=None, radius=0.3)
    d.tb(s, 0.95, 4.38, 8.1, 0.42, 'Next sprint: a deposit test for price, and warm channels for reach', size=11.5, bold=True, color=WHITE, anchor='m', align='c')

    # 12 Appendix: data
    s = d.slide('CONTENT', 'Appendix: The Numbers', notes="Not presented. Source: the shop logs every step to our Google Form response sheet; rows our team made with the test link are excluded. A visitor is counted once, by the first link they arrived through. Limits: a few visits arrive in the same second and are probably Instagram’s link checker, and we cannot rule out that a checkout click came from a friend of the team. PostHog (with session replays) has recorded the same events since Nov 17.")
    hdr = ['', 'Visitors', 'Add to cart', 'Checkout clicks', 'Checkout rate', 'Waitlist']
    rows = [(f'Shown ${p}', *P[p], pct(P[p][2], P[p][0]), '0') for p in (129, 169, 199)] + [(n.split(' (')[0], v, a, co, pct(co, v), '0') for n, v, a, co in ch] + [('All visitors', V, ATC, CO, pct(CO, V), str(DATA['waitlist']))]
    xs = [0.75, 3.35, 4.5, 5.75, 7.15, 8.4]; ws = [2.6, 1.1, 1.2, 1.35, 1.2, 0.85]
    for j, h in enumerate(hdr): d.tb(s, xs[j], 1.3, ws[j], 0.3, h, size=9, bold=True, color=CORAL, align='l' if j == 0 else 'r', anchor='m')
    for i, r in enumerate(rows):
        y = 1.62 + i * 0.36; last = i == len(rows) - 1
        d.box(s, 0.75, y, 8.5, 0.32, fill=INK if last else (PEACH if i % 2 == 0 else WHITE), line=None, radius=0.2)
        for j, v in enumerate(r): d.tb(s, xs[j] + (0.12 if j == 0 else 0), y, ws[j] - 0.12, 0.32, str(v), size=10, bold=(j == 0 or last), color=WHITE if last else INK, align='l' if j == 0 else 'r', anchor='m')
    d.tb(s, 0.75, 4.2, 8.5, 0.6, '', lines=[(f'Shop data, {DATA["asof"]}. Team test visits are excluded. Each visitor is counted once, by the first link they came through.', dict(size=9, color=GREY)), ('Limits: some same-second visits are probably Instagram’s link checker; a checkout click could be a friend of the team; clicks are not payments.', dict(size=9, color=GREY))], spacing=2)

    # 13 Appendix: unit economics math
    s = d.slide('CONTENT', 'Appendix: Unit Economics Math', notes="Not presented. Every assumption behind the unit economics slide. Cost to make is the top of our $60–80 estimate at 1,000 units from the Sprint 2 technical design; a sterling silver version would add $35–50.")
    left = [('Price (single bracelet)', f'${PRICE}'), ('Cost to make, at 1,000 units (top of $60–80 range)', f'−${COGS}'), ('Card fees (about 3%)', f'−${FEES}'), ('Packaging and shipping', f'−${SHIP}'), ('Returns and warranty reserve', f'−${RET}'), ('Contribution per bracelet = LTV (one purchase)', f'${MARGIN}')]
    for i, (k, v) in enumerate(left):
        y = 1.32 + i * 0.4; last = i == len(left) - 1
        d.box(s, 0.75, y, 4.6, 0.35, fill=INK if last else (PEACH if i % 2 == 0 else WHITE), line=None, radius=0.2)
        d.tb(s, 0.9, y, 3.5, 0.35, k, size=9.5, bold=last, color=WHITE if last else INK, anchor='m'); d.tb(s, 4.3, y, 0.95, 0.35, v, size=10.5, bold=True, color=WHITE if last else INK, anchor='m', align='r')
    right = [('Max CAC for LTV : CAC of 3 : 1', f'${MARGIN} ÷ 3 = ${MARGIN // 3}'), ('Assumed: checkout clicks that become purchases', '1 in 3'), ('Max cost per checkout click', f'${MARGIN // 3} ÷ 3 ≈ ${MARGIN / 9:.0f}'),
             ('Measured checkout rate, all visitors', f'{CO} ÷ {V} = {pct(CO, V)}'), ('So the most we can pay per visit', f'${MARGIN / 9 * CO / V:.2f}'), ('Paid ads: cost per visit', (f'${AD_SPEND / paid[1]:.2f}' if AD_SPEND else TODO)), ('Paid ads: checkout clicks', f'0 of {paid[1]}')]
    for i, (k, v) in enumerate(right):
        y = 1.32 + i * 0.4
        d.box(s, 5.55, y, 3.7, 0.35, fill=PEACH if i % 2 == 0 else WHITE, line=None, radius=0.2)
        d.tb(s, 5.68, y, 2.35, 0.35, k, size=9, anchor='m'); d.tb(s, 7.7, y, 1.45, 0.35, v, size=10, bold=True, anchor='m', align='r', color=CORAL if v == TODO else INK)
    d.tb(s, 0.75, 4.25, 8.5, 0.5, '', lines=[('The “1 in 3” purchase rate is our assumption, not a measurement; a deposit test would replace it. One-time purchase, so no repeat revenue is counted.', dict(size=9, color=GREY)), ('Upside not counted: pack orders (1 of 3 checkout carts was a 2-pack) and friends buying to join a group.', dict(size=9, color=GREY))], spacing=2)

    # 14 Appendix: benchmarks and sources
    s = d.slide('CONTENT', 'Appendix: Benchmarks and Sources', notes="Not presented. Where the comparison prices and the test setup come from.")
    rows = [('invisaWear safety charm', '$49 (listed at $99)', 'Sends an alert through your phone. No friend finding.'),
            ('Apple AirTag', '$29', 'Finds things, not friends, and needs phones nearby.'),
            ('She’s Birdie personal alarm', 'Sold to students via campus pages', 'A loud alarm. Same audience, same channels as ours.'),
            ('Firefly', f'${PRICE}, no monthly fee', 'Finds friends and says “I’m home” with a dead phone.')]
    for i, (a, b, cc) in enumerate(rows):
        y = 1.35 + i * 0.5; last = i == len(rows) - 1
        d.box(s, 0.75, y, 8.5, 0.44, fill=INK if last else (PEACH if i % 2 == 0 else WHITE), line=None, radius=0.2)
        for txt, xx, w, b_ in [(a, 0.9, 2.5, True), (b, 3.4, 2.3, False), (cc, 5.7, 3.45, False)]: d.tb(s, xx, y, w, 0.44, txt, size=10, bold=b_, color=WHITE if last else INK, anchor='m')
    d.tb(s, 0.75, 3.5, 8.5, 1.25, '', lines=[('SOURCES', dict(size=9, bold=True, color=CORAL)),
        ('Shop and test: ' + SITE + ' · responses in our Google Form sheet · PostHog dashboard and session replays (from Nov 17)', dict(size=9.5)),
        ('Prices: invisawear.com and apple.com (checked Nov 2026) · shesbirdie.com/pages/campus-lp', dict(size=9.5)),
        ('Costs: Sprint 2 technical design and parts list (firefly-band repo) · data plan about $10 for 10 years', dict(size=9.5)),
        ('Interviews and user test: Sprint 1 (12 interviews) and Sprint 2 (10 testers: 8 of 10 found a friend, 9 of 10 pressed “I’m home” first)', dict(size=9.5))], spacing=4)
    return d.finish()

if __name__ == '__main__':
    print(build())
