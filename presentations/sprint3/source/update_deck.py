"""Daily refresh of the Sprint 3 Google Slides deck from PostHog analytics.

Inputs  : presentations/sprint3/data/posthog.json  (written by whoever runs the PostHog query, see README)
Outputs : presentations/sprint3/charts/{price,channel,table}.png   charts shown on slides 4, 8 and 12
          presentations/sprint3/data/requests.json                  Google Slides batchUpdate requests
          presentations/sprint3/data/summary.md                     plain-English summary of the update
          presentations/sprint3/data/state.json                     what the deck currently says (updated with --commit-state)

Usage:
  python3 update_deck.py charts            # 1. render the charts from the data
  (commit and push, note the commit SHA)
  python3 update_deck.py requests <SHA>    # 2. write requests.json (text, notes, chart images at that commit)
  (send requests.json to the deck with the Google Slides connector)
  python3 update_deck.py commit-state      # 3. record that the deck now shows the new values, then commit and push
"""
import json, math, os, sys
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__)); ROOT = os.path.dirname(HERE)
DATA_DIR = ROOT + '/data'; CH = ROOT + '/charts'; os.makedirs(DATA_DIR, exist_ok=True); os.makedirs(CH, exist_ok=True)
DECK = '1YdcjysQXlJTmz-IwymgIBuPC0ltlp4hAPMTVNqiaGbM'
RAW = 'https://raw.githubusercontent.com/wendyxlin/firefly-band/{sha}/presentations/sprint3/charts/{name}.png'
IMG_IDS = {'price': 'ff_chart_price', 'channel': 'ff_chart_channel', 'table': 'ff_chart_table'}
NOTES_IDS = {p: f'{p}:notes_i3' for p in ('p4', 'p5', 'p8', 'p9', 'p10')}
PRICE, COGS, FEES, SHIP, RET = 169, 80, 5, 10, 8
MARGIN = PRICE - COGS - FEES - SHIP - RET

# Shop log (Google Form) for Nov 12 to Nov 17 4:00 PM ET, before PostHog was switched on. Team test visits excluded.
# (price, channel): (visitors, add to cart, checkout clicks, waitlist emails)
BASE = {('129', 'organic'): (9, 0, 0, 0), ('129', 'paid'): (31, 0, 0, 0), ('169', 'organic'): (10, 0, 0, 0), ('169', 'paid'): (26, 0, 0, 0),
        ('199', 'organic'): (9, 1, 1, 0), ('199', 'other'): (1, 0, 0, 0), ('199', 'paid'): (33, 0, 0, 0)}
# What the deck said when it was first uploaded (so the first run knows which text to replace).
SNAPSHOT = dict(asof='Nov 12–17 (as of Nov 17, 4:25 PM)', price={'129': (45, 0, 0), '169': (38, 1, 1), '199': (51, 2, 2)},
                chan={'paid': (93, 0, 0), 'organic': (30, 3, 3), 'other': (11, 0, 0)}, wait=0, expanded=0)

def pct(a, b): return (f'{100 * a / b:.1f}'.rstrip('0').rstrip('.') + '%') if b else '0%'

def load():
    """Baseline shop log + PostHog rows -> one data dict."""
    ph = json.load(open(DATA_DIR + '/posthog.json'))
    cells = {k: list(v) + [0] for k, v in BASE.items()}
    for price, chan, v, a, c, w, ex in ph['rows']:
        k = (str(price), chan if chan in ('paid', 'organic') else 'other'); cur = cells.setdefault(k, [0, 0, 0, 0, 0])
        for i, x in enumerate((v, a, c, w, ex)): cur[i] += int(x)
    d = dict(asof=f"Nov 12–{ph['range_end'].split(' ')[-1]} (as of {ph['asof_label']})", price={}, chan={}, wait=0, expanded=0)
    for p in ('129', '169', '199'): d['price'][p] = tuple(sum(v[i] for k, v in cells.items() if k[0] == p) for i in range(3))
    for ch in ('paid', 'organic', 'other'): d['chan'][ch] = tuple(sum(v[i] for k, v in cells.items() if k[1] == ch) for i in range(3))
    d['wait'] = sum(v[3] for v in cells.values()); d['expanded'] = sum(v[4] for v in cells.values())
    return d

def totals(d):
    return (sum(v[0] for v in d['price'].values()), sum(v[1] for v in d['price'].values()), sum(v[2] for v in d['price'].values()))

# ------------------------------------------------------------------ text on the slides
def strings(d):
    V, ATC, CO = totals(d); P = d['price']; paid, org, oth = d['chan']['paid'], d['chan']['organic'], d['chan']['other']
    share = round(100 * paid[0] / V) if V else 0
    s = {}
    s['t4_title'] = f'Revenue Test: {CO} of {V} Clicked Checkout'
    s['asof'] = f"Shop data, {d['asof']}"
    s['l4a'] = f'{pct(CO, V)} clicked checkout. Our bar was 10%.'
    if P['129'][2] == 0 and CO > 0: s['l4b'] = 'Price was not the blocker: 0 clicks at $129.'
    else: s['l4b'] = f"By price: {pct(P['129'][2], P['129'][0])} at $129, {pct(P['169'][2], P['169'][0])} at $169, {pct(P['199'][2], P['199'][0])} at $199."
    s['l4c'] = f"{d['wait']} of {CO} joined the waitlist afterwards."
    s['s5a'] = f'Solid: {V} real visitors, random prices, set bar.'
    s['s5b'] = f'Weak: {CO} clicks cannot rank three prices.'
    s['t8_title'] = 'GTM Test: Ads Brought Traffic, Not Buyers' if paid[2] == 0 else 'GTM Test: Followers Convert Better Than Ads'
    s['l8a'] = f'Paid: {share}% of visitors, 0 add-to-carts.' if paid[1] == 0 else f'Paid: {share}% of visitors, {paid[2]} checkout clicks ({pct(paid[2], paid[0])}).'
    s['l8b'] = f'Followers: {pct(org[2], org[0])} clicked checkout, ' + ('our 10% bar.' if org[0] and org[2] / org[0] >= 0.0995 else 'under our 10% bar.')
    s['s9a'] = (f'Fairly sure: cold ads do not convert yet ({paid[0]} visits, 0 carts).' if paid[1] == 0 else f'Cold ads convert weakly ({paid[0]} visits, {paid[2]} checkout clicks).')
    s['s9c'] = f'Organic is {org[0]} visitors, and some may be friends.'
    s['u10org'] = f'$0 · {org[2]} clicks'
    s['u10paid'] = f'[add] · {paid[2]} clicks'
    s['m13a'] = f'{CO} ÷ {V} = {pct(CO, V)}'
    s['m13b'] = f'${MARGIN / 9 * CO / V:.2f}' if V else '$0.00'
    s['m13c'] = f'{paid[2]} of {paid[0]}'
    return s

def notes(d, prev):
    V, ATC, CO = totals(d); P = d['price']; paid, org, oth = d['chan']['paid'], d['chan']['organic'], d['chan']['other']
    pv, pa, pc = totals(prev) if prev else (V, ATC, CO)
    day = f" Since the last update: {V - pv} more visitors and {CO - pc} more checkout clicks." if prev and (V != pv or CO != pc) else ''
    share = round(100 * paid[0] / V) if V else 0
    best = [f'${p}' for p in ('129', '169', '199') if P[p][2] > 0]
    price_line = (f"The surprise: nobody clicked at the cheapest price. All {CO} clicks were at {' and '.join(best)}, so price was not what stopped people." if P['129'][2] == 0 and CO > 0
                  else f"By price, checkout rates were {pct(P['129'][2], P['129'][0])} at $129, {pct(P['169'][2], P['169'][0])} at $169 and {pct(P['199'][2], P['199'][0])} at $199.")
    n = {}
    n['p4'] = (f"1:10–1:45. WILLINGNESS-TO-PAY RESULT. Each dot is one real visitor; coral dots clicked checkout. {V} visitors, {CO} checkout clicks: {pct(CO, V)}, "
               + ("well under our 10% bar. " if V and CO / V < 0.1 else "at or above our 10% bar. ") + price_line
               + f" {d['wait']} of the {CO} left an email for the waitlist. What we changed because of this: we removed the price question nobody answered, rebuilt the out-of-stock screen around the waitlist, and added a Show more section and session replays so we can see where people drop off."
               + f" Data: {d['asof']}." + day)
    n['p5'] = (f"1:45–2:10. Confidence is low to medium. We are confident most cold visitors will not buy at any of these prices. We are not confident about which price is best: {CO} clicks cannot rank three prices, and a click is not a payment. "
               "Next we would test a $10 refundable deposit, which is real money; a parent as the payer; a payment plan; and a cheaper version without cellular. Verdict: the model is plausible but not proven. $169 keeps a healthy margin, but demand at that price is unproven.")
    paid_line = (f"Paid ads brought {paid[0]} of our {V} visitors, about {share}% of the traffic, and not one added to cart." if paid[1] == 0
                 else f"Paid ads brought {paid[0]} of our {V} visitors, about {share}% of the traffic, and {paid[2]} checkout clicks: {pct(paid[2], paid[0])}.")
    n['p8'] = (f"3:00–3:35. CUSTOMER ACQUISITION RESULT. {paid_line} Organic Instagram, people who came through the link in our bio, brought {org[0]} visitors and {org[2]} checkout clicks: {pct(org[2], org[0])}. "
               f"Other sources brought {oth[0]} visitors and {oth[2]} checkout clicks. So a cold audience scrolling past an ad does not buy a ${PRICE} bracelet on first sight, but people who already follow us do click. "
               "What we changed: we moved the shop to a clean link, wearfirefly, because the old one showed a personal GitHub name; we set up a live dashboard that splits every visit by ad and channel; and we are moving effort from cold ads to warm channels. "
               f"Data: {d['asof']}." + day + " FILL IN the ad spend from Instagram before presenting.")
    n['p9'] = (f"3:35–4:00. " + (f"We are fairly confident that cold paid ads do not convert yet: {paid[0]} visitors and zero carts." if paid[1] == 0 else f"Cold paid ads convert weakly: {paid[0]} visitors and {paid[2]} checkout clicks.")
               + f" But it was two ads over a few days, so we have not tested many messages. We are less confident in the organic number: {org[0]} visitors is small, and some are probably friends of the team. "
               "Next we would test the warm channels we already tagged: group chats and flyers, a referral code for friend groups, a parent gift ad before the holidays, and showing ads again to people who already visited. Verdict: not a strong go-to-market yet. The channel that converts is small, and the channel that scales does not convert.")
    n['p10'] = (f"4:00–4:35. The product side works. At ${PRICE}, after about ${COGS} to make, ${FEES} in card fees, ${SHIP} shipping and ${RET} for returns, we keep about ${MARGIN} per bracelet. It is a one-time purchase, so that ${MARGIN} is the lifetime value. "
                f"For a healthy three-to-one ratio we can spend at most ${MARGIN // 3} to win a customer. If one in three checkout clicks becomes a purchase, that means about ${MARGIN / 9:.0f} per checkout click. "
                f"Our followers gave us {org[2]} checkout clicks for free, but paid ads produced {paid[2]} checkout clicks from {paid[0]} visits, so " + ("paid acquisition cost is not measurable yet. " if paid[2] == 0 else "paid acquisition is still far from the target. ")
                + "Conclusion: we would make money on each bracelet, but we have not shown we can buy customers for less than we earn. The math is in the appendix.")
    return n

# ------------------------------------------------------------------ charts
S = 400   # pixels per inch while drawing (downsampled by 2 on save)
INK, CORAL, BLUSH, PEACH, GREY, TEAL, ORANGE, WHITE = '#000000', '#F55F39', '#F1B0A7', '#F8D9CA', '#555555', '#3BADB1', '#EA9F3F', '#FFFFFF'
def font(pt, bold=False):
    for f in (['LiberationSans-Bold.ttf', 'Arial Bold.ttf', 'DejaVuSans-Bold.ttf'] if bold else ['LiberationSans-Regular.ttf', 'Arial.ttf', 'DejaVuSans.ttf']):
        for d in ('/usr/share/fonts/truetype/liberation/', '/usr/share/fonts/truetype/dejavu/', '/Library/Fonts/', '/System/Library/Fonts/Supplemental/', ''):
            try: return ImageFont.truetype(d + f, int(pt * S / 72))
            except Exception: pass
    return ImageFont.load_default()

class Canvas:
    def __init__(self, w, h): self.im = Image.new('RGBA', (int(w * S), int(h * S)), (0, 0, 0, 0)); self.d = ImageDraw.Draw(self.im)
    def card(self, x, y, w, h, fill=WHITE, line=INK, r=0.13):
        self.d.rounded_rectangle([x * S, y * S, (x + w) * S, (y + h) * S], radius=r * S, fill=fill, outline=line, width=int(S * 0.012) if line else 0)
    def text(self, x, y, s, pt, bold=False, color=INK, align='l', w=0):
        f = font(pt, bold); tw = self.d.textlength(s, font=f)
        xx = x * S if align == 'l' else (x + w) * S - tw if align == 'r' else (x + w / 2) * S - tw / 2
        self.d.text((xx, y * S), s, font=f, fill=color); return tw / S
    def dots(self, x, y, w, h, n, hot):
        if n <= 0: return
        best = (0, 1)
        for cols in range(1, 80):
            rows = math.ceil(n / cols); p = min(w / cols, h / rows, 0.24)
            if p > best[0] + 1e-9: best = (p, cols)
        p, cols = best; dia = p * 0.77
        for i in range(n):
            cx, cy = x + (i % cols) * p, y + (i // cols) * p
            self.d.ellipse([cx * S, cy * S, (cx + dia) * S, (cy + dia) * S], fill=CORAL if i >= n - hot else BLUSH)
    def save(self, name):
        im = self.im.resize((self.im.width // 2, self.im.height // 2), Image.LANCZOS); im.save(f'{CH}/{name}.png', optimize=True)

def charts(d):
    V, ATC, CO = totals(d)
    c = Canvas(8.5, 2.2)
    for i, p in enumerate(('129', '169', '199')):
        v, a, co = d['price'][p]; x = i * 2.88
        c.card(x + 0.01, 0.01, 2.72, 2.18)
        c.text(x + 0.16, 0.1, f'${p}', 20, True)
        c.text(x + 0.16, 0.1, f'{co} of {v}', 13, True, CORAL if co else GREY, 'r', 2.42)
        c.text(x + 0.16, 0.34, 'clicked checkout', 8.5, False, GREY, 'r', 2.42)
        c.dots(x + 0.19, 0.64, 2.4, 1.44, v, co)
    c.save('price')
    c = Canvas(8.5, 2.2)
    for (key, name, col), (x, w) in zip([('paid', 'PAID INSTAGRAM ADS', ORANGE), ('organic', 'INSTAGRAM ORGANIC', TEAL), ('other', 'OTHER', GREY)], [(0, 3.7), (3.9, 2.55), (6.65, 1.85)]):
        v, a, co = d['chan'][key]
        c.card(x + 0.01, 0.01, w - 0.02, 2.18)
        c.text(x + 0.16, 0.1, name, 9, True, col)
        tw = c.text(x + 0.16, 0.3, f'{co} of {v}', 17, True, CORAL if co else INK)
        c.text(x + 0.16, 0.62, 'clicked checkout' + (f'  ·  {pct(co, v)}' if co else ''), 9, False, GREY)
        c.dots(x + 0.19, 0.92, w - 0.38, 1.16, v, co)
    c.save('channel')
    c = Canvas(8.5, 2.85)
    xs = [0, 2.6, 3.75, 5.0, 6.4, 7.65]; ws = [2.6, 1.1, 1.2, 1.35, 1.2, 0.85]
    for j, h in enumerate(['', 'Visitors', 'Add to cart', 'Checkout clicks', 'Checkout rate']):
        if h: c.text(xs[j], 0.08, h, 9, True, CORAL, 'r', ws[j] - 0.12)
    rows = [(f'Shown ${p}', *d['price'][p]) for p in ('129', '169', '199')] + [(n, *d['chan'][k]) for k, n in (('paid', 'Paid Instagram ads'), ('organic', 'Instagram organic'), ('other', 'Other'))] + [('All visitors', V, ATC, CO)]
    for i, (lab, v, a, co) in enumerate(rows):
        y = 0.32 + i * 0.33; last = i == len(rows) - 1
        c.card(0, y, 8.5, 0.29, fill=INK if last else (PEACH if i % 2 == 0 else WHITE), line=None, r=0.07)
        col = WHITE if last else INK
        c.text(0.12, y + 0.065, lab, 10, True, col)
        for j, val in enumerate((v, a, co, pct(co, v)), start=1): c.text(xs[j], y + 0.065, str(val), 10, last, col, 'r', ws[j] - 0.12)
    y = 0.32 + len(rows) * 0.33 + 0.05
    c.text(0.12, y, f"Waitlist emails: {d['wait']}    ·    Opened “Show more” (tracked since Nov 17): {d['expanded']} visitors", 9.5, False, GREY)
    c.save('table')

# ------------------------------------------------------------------ requests
def state():
    p = DATA_DIR + '/state.json'
    if os.path.exists(p): return json.load(open(p))
    return dict(data=SNAPSHOT, strings=strings(SNAPSHOT), notes={})

def requests(sha):
    d = load(); st = state(); new = strings(d); old = st['strings']
    prev = st['data'] if st.get('notes') else None
    reqs = []; changed = {k: (old.get(k), v) for k, v in new.items() if old.get(k) != v}
    two_phase = bool({v[1] for v in changed.values()} & {v[0] for v in changed.values()})
    order = sorted(changed, key=lambda k: -len(changed[k][0] or ''))
    rep = lambda a, b: {'replaceAllText': {'containsText': {'text': a, 'matchCase': True}, 'replaceText': b}}
    if two_phase:
        reqs += [rep(changed[k][0], f'[[{k}]]') for k in order]; reqs += [rep(f'[[{k}]]', changed[k][1]) for k in order]
    else:
        reqs += [rep(changed[k][0], changed[k][1]) for k in order]
    for name, oid in IMG_IDS.items():
        reqs.append({'replaceImage': {'imageObjectId': oid, 'url': RAW.format(sha=sha, name=name), 'imageReplaceMethod': 'CENTER_INSIDE'}})
    nn = notes(d, prev)
    for pid, text in nn.items():
        if st.get('notes', {}).get(pid) != text:
            reqs += [{'deleteText': {'objectId': NOTES_IDS[pid], 'textRange': {'type': 'ALL'}}}, {'insertText': {'objectId': NOTES_IDS[pid], 'insertionIndex': 0, 'text': text}}]
    json.dump(reqs, open(DATA_DIR + '/requests.json', 'w'), ensure_ascii=False, indent=0)
    json.dump(dict(data=d, strings=new, notes=nn), open(DATA_DIR + '/state.next.json', 'w'), ensure_ascii=False, indent=1)
    V, ATC, CO = totals(d); pv, pa, pc = totals(st['data'])
    P = d['price']; C = d['chan']
    lines = [f"# Sprint 3 deck update, {d['asof']}", '',
             f"- Total: {V} visitors, {ATC} add-to-carts, {CO} checkout clicks ({pct(CO, V)}), {d['wait']} waitlist emails, {d['expanded']} opened Show more.",
             f"- Change since the deck last said: {V - pv:+d} visitors, {CO - pc:+d} checkout clicks.",
             '- Willingness to pay, by price shown: ' + '; '.join(f"${p}: {P[p][2]} of {P[p][0]} ({pct(P[p][2], P[p][0])})" for p in ('129', '169', '199')) + '.',
             '- Customer acquisition, by channel: ' + '; '.join(f"{n}: {C[k][2]} of {C[k][0]} ({pct(C[k][2], C[k][0])})" for k, n in (('paid', 'paid ads'), ('organic', 'Instagram organic'), ('other', 'other'))) + '.',
             f"- Text changed on the slides: {len(changed)} line(s); charts on slides 4, 8 and 12 replaced; requests: {len(reqs)}."]
    flags = []
    if (st['data']['chan']['paid'][2] == 0) != (C['paid'][2] == 0): flags.append('Paid ads now have checkout clicks: the GTM and unit economics conclusions (slides 8, 9, 10, 11) need a human read.')
    if (st['data']['price']['129'][2] == 0) != (P['129'][2] == 0): flags.append('The $129 price now has checkout clicks: the "price was not the blocker" conclusion (slides 4, 5) needs a human read.')
    if V and CO / V >= 0.1: flags.append('Overall checkout rate is at or above the 10% bar: slides 4, 5 and 10 conclusions need a human read.')
    if flags: lines += ['', '## Needs a human read'] + [f'- {f}' for f in flags]
    open(DATA_DIR + '/summary.md', 'w').write('\n'.join(lines) + '\n'); print('\n'.join(lines)); print(f'\nrequests.json: {len(reqs)} requests, {os.path.getsize(DATA_DIR + "/requests.json")} bytes')

if __name__ == '__main__':
    cmd = sys.argv[1] if len(sys.argv) > 1 else ''
    if cmd == 'charts': charts(load()); print('charts written to', CH)
    elif cmd == 'requests': requests(sys.argv[2])
    elif cmd == 'commit-state': os.replace(DATA_DIR + '/state.next.json', DATA_DIR + '/state.json'); print('state updated')
    else: print(__doc__)
