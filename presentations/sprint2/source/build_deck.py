"""Build the two Sprint 2 decks (Afterglow watch, Firefly v2 bracelet) on the team's Sprint2_Presentation_v4 template.
Usage: python build_deck.py watch|bracelet  -> out/<name>.pptx"""
import copy, os, sys
from pptx import Presentation
from pptx.util import Inches, Pt, Emu
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from PIL import Image
import qrcode

SC = '/tmp/claude-0/-home-claude/05671788-1db4-51ad-86c7-0131427b2680/scratchpad'
DK = SC + '/deck'; REC = DK + '/rec'; TPL = DK + '/tplimg'; OUT = DK + '/out'; os.makedirs(OUT, exist_ok=True); os.makedirs(DK + '/tmp', exist_ok=True)
INK = RGBColor(0, 0, 0); CREAM = RGBColor(0xF1, 0xEE, 0xE8); CORAL = RGBColor(0xF5, 0x5F, 0x39); ORANGE = RGBColor(0xEA, 0x9F, 0x3F)
TEAL = RGBColor(0x3B, 0xAD, 0xB1); BLUSH = RGBColor(0xF1, 0xB0, 0xA7); PEACH = RGBColor(0xF8, 0xD9, 0xCA); GREY = RGBColor(0x55, 0x55, 0x55); WHITE = RGBColor(255, 255, 255)
GREEN = RGBColor(0x2F, 0x8A, 0x5F); RED = RGBColor(0xC6, 0x2E, 0x3D)
REPO = 'https://wendyxlin.github.io/firefly-band'
TEAM = 'Wendy, Ava, Yvonne, Lucas'

AW = SC + '/aw/v2-bracelet'; VB = SC + '/v2/site'
D = {
 'watch': dict(
    file='Sprint2_Presentation_Afterglow_Watch', name='Afterglow', kind='watch',
    oneliner='A dress watch with two hidden buttons: I’m Home and SOS', tag='Stay close. Go out.',
    hero=AW + '/renders/v2-hero.jpg', buttons=AW + '/renders/v2-buttons.jpg', h1=AW + '/renders/app-friends.jpg', h1_phone=True, h2=AW + '/renders/v2-home.jpg',
    lights=[AW + '/renders/v2-apart.jpg', AW + '/renders/v2-home.jpg', AW + '/renders/v2-sos.jpg'], lights_cap=['Drifted apart', 'I’m Home', 'SOS'],
    app=[AW + '/renders/app-home.jpg', AW + '/renders/app-friends.jpg', AW + '/renders/app-checkins.jpg'],
    film=REC + '/watch-film-30s.mp4', film_poster=REC + '/watch-film-poster.jpg', film_full=REPO + '/afterglow-watch/media/afterglow-promo.mp4',
    appdemo=REC + '/watch-app-demo.mp4', appdemo_poster=REC + '/watch-app-poster.jpg', sitedemo=REC + '/watch-site-demo.mp4', sitedemo_poster=REC + '/watch-site-poster.jpg',
    mockup=REC + '/watch-mockup.png', site_url=REPO + '/afterglow-watch/', app_url=REPO + '/afterglow-watch/app/',
    meet=[('Crown · 3 o’clock', 'Press = I’m Home. Press again within 5 s = cancel.', GREEN),
          ('Pusher · 2 o’clock (red ring)', 'Hold 3 s = SOS. Press twice in the grace window = cancel.', RED),
          ('Mother-of-pearl dial', 'Lights through the markers: lavender (apart), green (home), red (SOS).', ORANGE),
          ('Radios under the dial', 'UWB (0–30 m) · LoRa (1 km) · LTE-M (6+ mi). Antennas in the strap.', TEAL)],
    meet_badge='34 mm · ~30 g · ~13 h heavy night',
    cards=[('CROWN · I’M HOME', GREEN, [('●', 'Press', 'I’m Home to the circle'), ('●●', 'Press again ≤ 5 s', 'Cancel')]),
           ('PUSHER · SOS', RED, [('▬ 3 s', 'Hold', 'SOS + live location'), ('●●', 'Press twice', 'Cancel (5–10 s grace)')])],
    cards_foot='Automatic: separation alert (10–30 m radius, 1/2/5 min delay)  ·  In the app: Find friends, Come Find Me',
    process=[('/home/claude/firefly-band/media/renders/firefly-product-champagne.png', 'v1 · Bangle'), ('/home/claude/firefly-band/docs/watch/renders/watch-hero.jpg', 'Watch · Find + Safety'), (AW + '/renders/v2-hero.jpg', 'Afterglow · Home + SOS')],
    decision='Hide it in a watch. Two buttons only: crown = I’m Home, pusher = SOS. Finding moved to the app.',
    cut='Find and Come Find Me buttons (now in the app), maps up close, accounts and logins.',
    surprise='No wrist radio reaches 6 miles, so we added LTE-M cellular, with Sidewalk as a fallback.',
    redo='Lock the form factor before building every output: we rebuilt them three times.',
    risk='Weight (~32 g as drawn vs. 29 g target) and 13 h of battery on a heavy night.',
    next=[('Dev-board prototype', 'UWB + LoRa + LTE-M on two wrists'), ('Bar test', '10 testers, real venue, real basement'), ('Shrink + certify', 'Custom PCB, FCC, carrier approval')],
    feas=[('Range ≥ 6 mi, weak signal', 'Feasible: LTE-M/NB-IoT (nRF9151), ~20 dB better than phone LTE'), ('Up-close distance', 'UWB (DW3110): reliable 10–20 m in a crowd'),
          ('Battery', '210 mAh round cell: ~13 h heavy night, ~45 h typical'), ('Weight', '~32 g as drawn; ~29 g with 32 mm case + thinner strap'),
          ('Open risks', 'Light through the dial; marker direction outdoors only; certification'), ('Prototype cost', '~$247 per watch on dev boards')]),
 'bracelet': dict(
    file='Sprint2_Presentation_Firefly_v2_Bracelet', name='Firefly', kind='bracelet',
    oneliner='A slim bracelet that finds your friends and tells them you’re home, even when your phones die', tag='Stay connected. Go further together.',
    hero=VB + '/renders/v2-hero.jpg', buttons=VB + '/renders/v2-buttons.jpg', h1=VB + '/renders/v2-find.jpg', h1_phone=False, h2=VB + '/renders/v2-home.jpg',
    lights=[VB + '/renders/v2-find.jpg', VB + '/renders/v2-home.jpg', VB + '/renders/v2-sos.jpg'], lights_cap=['Finding', 'I’m home', 'SOS'],
    app=[VB + '/renders/app-group.jpg', VB + '/renders/app-find.jpg', VB + '/renders/app-checkins.jpg'],
    film=REC + '/bracelet-film-30s.mp4', film_poster=REC + '/bracelet-film-poster.jpg', film_full=REPO + '/v2-bracelet/media/firefly-v2-promo.mp4',
    appdemo=REC + '/bracelet-app-demo.mp4', appdemo_poster=REC + '/bracelet-app-poster.jpg', sitedemo=REC + '/bracelet-site-demo.mp4', sitedemo_poster=REC + '/bracelet-site-poster.jpg',
    mockup=REC + '/bracelet-mockup.png', site_url=REPO + '/v2-bracelet/', app_url=REPO + '/v2-bracelet/app/',
    meet=[('Button 1 · engraved dot', 'Press = find friends. Press twice = come find me.', CORAL),
          ('The light', 'Pink (finding), amber (come find me), green (home), red (SOS).', ORANGE),
          ('Button 2 · engraved line', 'Press = I’m home. Hold both 3 s = quiet SOS.', GREEN),
          ('Radios in the capsule', 'UWB · LoRa · LTE-M. The band is the antenna; 2nd battery in the clasp.', TEAL)],
    meet_badge='40 mm capsule · ~15 g · ~9 h heavy night',
    cards=[('BUTTON 1 · FIND', CORAL, [('●', 'Press', 'Find friends'), ('●●', 'Press twice', 'Come find me')]),
           ('BUTTON 2 · HOME', GREEN, [('●', 'Press', 'I’m home'), ('●●', 'Twice ≤ 5 s', 'Cancel')]),
           ('BOTH · SOS', RED, [('▬ 3 s', 'Hold both', 'Quiet SOS'), ('●●', 'Either, twice', 'Cancel in grace')])],
    cards_foot='Automatic: separation alert (10–30 m radius, 1/2/5 min delay)  ·  Colours: gold, silver, rose gold, black',
    process=[('/home/claude/firefly-band/media/renders/firefly-product-champagne.png', 'v1 · Bangle'), (AW + '/renders/v2-hero.jpg', 'Watch direction'), (VB + '/renders/v2-hero.jpg', 'v2 · Bracelet')],
    decision='Back to jewelry: two buttons + one light. SOS hidden as a both-buttons hold, so no third button.',
    cut='A screen, maps up close, accounts and logins, a separate SOS button.',
    surprise='No wrist radio reaches 6 miles, so we added LTE-M cellular. The battery had to split into capsule + clasp.',
    redo='Lock the form factor before building every output: we rebuilt them three times.',
    risk='Battery: 145 mAh across capsule + clasp gives ~9 h on a heavy night.',
    next=[('Dev-board prototype', 'UWB + LoRa + LTE-M on two wrists'), ('Bar test', '10 testers, real venue, real basement'), ('Shrink + certify', 'Custom PCB, FCC, carrier approval')],
    feas=[('Range ≥ 6 mi, weak signal', 'Feasible: LTE-M/NB-IoT (nRF9151), ~20 dB better than phone LTE'), ('Up-close distance', 'UWB (DW3110): reliable 10–20 m in a crowd'),
          ('Battery', '85 mAh capsule + 60 mAh clasp: ~9 h heavy night, ~31 h typical'), ('Weight', '~15 g in titanium, ~22 g in gold-plated brass'),
          ('Open risks', 'Band as antenna needs RF tuning; UWB through ceramic underside'), ('Prototype cost', '~$247 per bracelet on dev boards')]),
}

def fit_crop(src, w_in, h_in, focus=(0.5, 0.5), name=None):
    """Center-crop an image to the box aspect ratio (no stretching)."""
    im = Image.open(src); im = im.convert('RGBA') if im.mode in ('RGBA', 'LA', 'P') else im.convert('RGB')
    ar = w_in / h_in; W, H = im.size
    if W / H > ar: nw = int(H * ar); x0 = int((W - nw) * focus[0]); im = im.crop((x0, 0, x0 + nw, H))
    else: nh = int(W / ar); y0 = int((H - nh) * focus[1]); im = im.crop((0, y0, W, y0 + nh))
    out = DK + '/tmp/' + (name or (os.path.basename(src).rsplit('.', 1)[0] + f'_{int(w_in*100)}x{int(h_in*100)}')) + ('.png' if im.mode == 'RGBA' else '.jpg')
    im.save(out, quality=90) if im.mode != 'RGBA' else im.save(out); return out

class Deck:
    def __init__(self, cfg):
        self.c = cfg; self.p = Presentation(DK + '/template_v4.pptx'); self.n0 = len(self.p.slides._sldIdLst)
        self.L = {l.name: l for l in self.p.slide_layouts}
    def slide(self, layout, title=None, notes=''):
        s = self.p.slides.add_slide(self.L[layout])
        for ph in list(s.placeholders):
            if title is not None and ph.placeholder_format.type is not None and 'TITLE' in str(ph.placeholder_format.type):
                ph.text_frame.text = title; r = ph.text_frame.paragraphs[0].runs[0]; r.font.color.rgb = INK
            elif ph.placeholder_format.idx != 0 or title is None:
                ph._element.getparent().remove(ph._element)
        if notes: s.notes_slide.notes_text_frame.text = notes
        return s
    def tb(self, s, x, y, w, h, text, size=14, bold=False, color=INK, align='l', italic=False, anchor='t', lines=None, spacing=None):
        t = s.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h)); tf = t.text_frame; tf.word_wrap = True
        tf.margin_left = tf.margin_right = Inches(0.04); tf.margin_top = tf.margin_bottom = Inches(0.02)
        tf.vertical_anchor = {'t': MSO_ANCHOR.TOP, 'm': MSO_ANCHOR.MIDDLE, 'b': MSO_ANCHOR.BOTTOM}[anchor]
        items = lines or [(text, dict(size=size, bold=bold, color=color, italic=italic))]
        for i, (tx, st) in enumerate(items):
            para = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
            para.alignment = {'l': PP_ALIGN.LEFT, 'c': PP_ALIGN.CENTER, 'r': PP_ALIGN.RIGHT}[align]
            if spacing: para.space_after = Pt(spacing)
            r = para.add_run(); r.text = tx; f = r.font; f.name = 'Arial'; f.size = Pt(st.get('size', size)); f.bold = st.get('bold', bold); f.italic = st.get('italic', italic)
            f.color.rgb = st.get('color', color)
        return t
    def box(self, s, x, y, w, h, fill=None, line=INK, lw=0.75, shape=MSO_SHAPE.ROUNDED_RECTANGLE, radius=0.08):
        b = s.shapes.add_shape(shape, Inches(x), Inches(y), Inches(w), Inches(h))
        if shape == MSO_SHAPE.ROUNDED_RECTANGLE:
            try: b.adjustments[0] = radius
            except Exception: pass
        if fill is None: b.fill.background()
        else: b.fill.solid(); b.fill.fore_color.rgb = fill
        if line is None: b.line.fill.background()
        else: b.line.color.rgb = line; b.line.width = Pt(lw)
        b.shadow.inherit = False; b.text_frame.text = ''
        return b
    def circ(self, s, x, y, d, fill, text='', size=12, color=WHITE, bold=True):
        b = self.box(s, x, y, d, d, fill=fill, line=None, shape=MSO_SHAPE.OVAL)
        if text:
            tf = b.text_frame; tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0; tf.vertical_anchor = MSO_ANCHOR.MIDDLE
            p = tf.paragraphs[0]; p.alignment = PP_ALIGN.CENTER; r = p.add_run(); r.text = text; r.font.size = Pt(size); r.font.bold = bold; r.font.color.rgb = color; r.font.name = 'Arial'
        return b
    def pic(self, s, path, x, y, w, h, crop=True, focus=(0.5, 0.5), frame=False):
        src = fit_crop(path, w, h, focus) if crop else path
        p = s.shapes.add_picture(src, Inches(x), Inches(y), Inches(w), Inches(h))
        if frame: p.line.color.rgb = INK; p.line.width = Pt(0.75)
        return p
    def movie(self, s, path, poster, x, y, w, h):
        pf = fit_crop(poster, w, h, name=os.path.basename(poster).rsplit('.', 1)[0] + '_poster')
        m = s.shapes.add_movie(path, Inches(x), Inches(y), Inches(w), Inches(h), poster_frame_image=pf, mime_type='video/mp4')
        m.line.color.rgb = INK; m.line.width = Pt(0.75); return m
    def qr(self, s, url, x, y, d):
        fn = DK + '/tmp/qr_' + str(abs(hash(url))) + '.png'
        q = qrcode.QRCode(border=1, box_size=10); q.add_data(url); q.make(fit=True); q.make_image(fill_color='black', back_color='#F1EEE8').save(fn)
        return s.shapes.add_picture(fn, Inches(x), Inches(y), Inches(d), Inches(d))
    def finish(self):
        # drop the template's original slides (kept their layouts, theme and images we reused)
        lst = self.p.slides._sldIdLst
        for sid in list(lst)[:self.n0]:
            self.p.part.drop_rel(sid.rId); lst.remove(sid)
        fn = OUT + '/' + self.c['file'] + '.pptx'; self.p.save(fn); return fn

def build(key):
    c = D[key]; d = Deck(c); nm = c['name']; W_ = c['kind']
    # 1 Title
    s = d.slide('TITLE_L', notes=f"0:00–0:10. One sentence: “{nm} is {c['oneliner'][0].lower() + c['oneliner'][1:]}.” Then straight into the story.")
    d.tb(s, 0.75, 1.45, 5.0, 0.9, nm, size=54, bold=False)
    d.tb(s, 0.75, 2.35, 4.7, 1.0, c['oneliner'], size=16, color=GREY)
    d.tb(s, 0.75, 3.25, 4.7, 0.4, c['tag'], size=15, italic=True, color=CORAL)
    d.box(s, 0.75, 3.85, 4.4, 0.42, line=INK, radius=0.5); d.tb(s, 0.75, 3.85, 4.4, 0.42, TEAM, size=12, align='c', anchor='m')
    d.box(s, 5.75, 1.0, 3.6, 3.6, fill=PEACH, line=None, radius=0.06); d.pic(s, c['hero'], 5.9, 1.15, 3.3, 3.3, focus=(0.55, 0.45))
    # 2 Story
    s = d.slide('STATEMENT', notes="0:10–0:25. Tell it as a story: phones die, signal fails in packed bars, the group splits for Ubers and restrooms. Pause on the question.")
    d.tb(s, 0.75, 0.95, 4.6, 0.9, '11:47 PM', size=48)
    d.tb(s, 0.75, 2.0, 4.5, 1.6, '', lines=[('Your phone is at 3%.', dict(size=22)), ('No signal.', dict(size=22)), ('Where did Maya go?', dict(size=22, italic=True, color=CORAL))])
    d.pic(s, TPL + '/s2_55.png', 5.45, 1.1, 3.9, 3.58, crop=False)
    # 3 Discovery -> pivot
    s = d.slide('CONTENT', 'From Discovery to Building', notes="0:25–0:40. Key pivot from 12 Sprint 1 interviews. Finding friends already exists (Totem, Lynq, mostly festival products). The unsolved part: knowing everyone got home, and asking for help without a phone. Today one 'group parent' chases everyone.")
    d.pic(s, TPL + '/s4_71.png', 1.0, 1.35, 2.7, 2.7, crop=False); d.pic(s, TPL + '/s4_73.png', 5.9, 1.35, 2.7, 2.7, crop=False)
    a = d.box(s, 4.25, 2.45, 1.2, 0.5, fill=INK, line=None, shape=MSO_SHAPE.RIGHT_ARROW)
    d.tb(s, 0.75, 4.15, 3.6, 0.6, '', lines=[('DISCOVERY · 12 INTERVIEWS', dict(size=9, bold=True, color=GREY)), ('One friend chases everyone home', dict(size=13))])
    d.tb(s, 5.4, 4.15, 3.9, 0.6, '', lines=[('PIVOT', dict(size=9, bold=True, color=CORAL)), (f'Everyone checks in themselves, even with a dead phone', dict(size=13, color=CORAL))])
    # 4 Two bets + metrics
    s = d.slide('CONTENT', 'Two Bets, Two Bars', notes="0:40–0:55. H1 and H2 come from our usability test (Firefly_User_Test). Success bar for each: at least 8 of 10 testers. Say the bar, then move on: results come on the validation slide.")
    for i, (img, phone, hx, lab, bet, bar) in enumerate([(c['h1'], c['h1_phone'], 0.9, 'H1', 'Find a friend, no map?', '≥ 8/10 find a hidden friend using only the buzz / light / distance, no hints, in ≤ 120 s'),
                                                        (c['h2'], False, 5.25, 'H2', 'Say “I’m home” unprompted?', '≥ 8/10 press I’m home as their first action when the night ends')]):
        d.box(s, hx, 1.32, 3.85, 2.45, fill=PEACH, line=None, radius=0.06)
        if phone: d.pic(s, img, hx + 1.2, 1.37, 1.13, 2.35, focus=(0.5, 0.2))
        else: d.pic(s, img, hx + 0.1, 1.42, 3.65, 2.25, focus=(0.5, 0.5))
        d.circ(s, hx, 3.92, 0.5, CORAL if i == 0 else GREEN, lab, 13)
        d.tb(s, hx + 0.6, 3.88, 3.3, 0.35, bet, size=14, bold=True)
        d.tb(s, hx + 0.6, 4.2, 3.3, 0.55, bar, size=10.5, color=GREY)
    # 5 Meet
    s = d.slide('CONTENT', f'Meet {nm}', notes=f"0:55–1:15. Walk the four numbers. Everything you see is in the repo: 3D model, Cycles renders, technical design and parts list. {c['meet_badge']}.")
    d.box(s, 0.75, 1.3, 4.3, 3.45, fill=PEACH, line=None, radius=0.05); d.pic(s, c['buttons'], 0.85, 1.4, 4.1, 3.25, focus=(0.5, 0.5))
    for i, (h, sub, col) in enumerate(c['meet']):
        y = 1.38 + i * 0.8; d.circ(s, 5.35, y, 0.42, col, str(i + 1), 13)
        d.tb(s, 5.9, y - 0.05, 3.35, 0.32, h, size=13.5, bold=True); d.tb(s, 5.9, y + 0.25, 3.35, 0.45, sub, size=10.5, color=GREY)
    d.box(s, 5.35, 4.55, 3.1, 0.34, fill=INK, line=None, radius=0.5); d.tb(s, 5.35, 4.55, 3.1, 0.34, c['meet_badge'], size=10, color=WHITE, align='c', anchor='m', bold=True)
    # 6 Buttons
    title = 'Two Buttons, Zero Screens'
    s = d.slide('CONTENT', title, notes="1:15–1:35. Point at each row. " + ("Crown: press for I'm Home, press again within 5 s to cancel. Pusher: hold 3 s for SOS, press twice in the grace window to cancel. Finding a friend and Come Find Me live in the app; the separation alert is automatic." if W_ == 'watch' else "Button 1: press to find friends (buzz and light pulse faster as you get closer), press twice for come find me. Button 2: I'm home. Hold both for 3 s: quiet SOS, with a grace window to cancel. The separation alert is automatic."))
    n = len(c['cards']); cw = (8.5 - 0.25 * (n - 1)) / n
    for i, (hdr, col, rows) in enumerate(c['cards']):
        x = 0.75 + i * (cw + 0.25)
        d.box(s, x, 1.35, cw, 2.75, fill=WHITE, line=INK, radius=0.05)
        hb = d.box(s, x, 1.35, cw, 0.42, fill=col, line=INK, radius=0.25); d.tb(s, x + 0.15, 1.35, cw - 0.3, 0.42, hdr, size=11, bold=True, color=WHITE, anchor='m')
        for j, (glyph, how, what) in enumerate(rows):
            y = 2.0 + j * 0.95
            d.tb(s, x + 0.15, y, 0.95, 0.5, glyph, size=18 if len(glyph) < 4 else 13, bold=True, color=col, anchor='m')
            d.tb(s, x + 1.1, y - 0.02, cw - 1.2, 0.3, how, size=10, color=GREY); d.tb(s, x + 1.1, y + 0.24, cw - 1.2, 0.35, what, size=14, bold=True)
    d.box(s, 0.75, 4.28, 8.5, 0.5, fill=PEACH, line=None, radius=0.3); d.tb(s, 0.95, 4.28, 8.1, 0.5, c['cards_foot'], size=10.5, anchor='m', align='c')
    # 7 Range + privacy
    s = d.slide('CONTENT', 'How It Reaches 6+ Miles', notes="1:35–1:50. No wrist-sized radio reaches 6 miles directly, so the device picks the best link: ultra-wideband up close, LoRa across a venue, LTE-M cellular beyond 1 km. LTE-M and NB-IoT are built for weak signal (about 20 dB more reach than phone LTE), so they get into basements. Fallback: Amazon Sidewalk. None of it needs the wearer's phone. Privacy: only your group, key expires at the end of the night, encrypted on the device.")
    segs = [('UWB', '0–30 m', 'Distance to the metre', TEAL, 1.6), ('LoRa', '30 m–1 km', 'Device to device, no network', ORANGE, 2.4), ('LTE-M cellular', '1 km–6+ mi', 'Built for one bar, basements', CORAL, 3.3)]
    x = 0.95; d.circ(s, 0.75, 2.12, 0.42, INK, 'you', 9)
    for lab, dist, sub, col, w in segs:
        d.box(s, x + 0.25, 2.2, w - 0.05, 0.26, fill=col, line=None, radius=0.5)
        d.tb(s, x + 0.25, 1.45, w, 0.35, dist, size=18, bold=True); d.tb(s, x + 0.25, 1.8, w, 0.3, lab, size=10, bold=True, color=col)
        d.tb(s, x + 0.25, 2.55, w, 0.5, sub, size=10, color=GREY); x += w
    d.tb(s, 0.75, 3.15, 8.5, 0.35, 'Fallback when there’s no signal at all: Amazon Sidewalk and passing phones  ·  I’m home and SOS never need your phone', size=10.5, color=GREY, align='c')
    for i, (img, cap) in enumerate([(TPL + '/s7_99.png', 'Only your group sees you'), (TPL + '/s7_99.png', 'Key expires at end of night'), (TPL + '/s7_101.png', 'Nothing stored on a server')]):
        xx = 0.95 + i * 2.85
        if i == 0:
            d.circ(s, xx, 3.95, 0.5, BLUSH, '♥', 16, INK)
        else: d.pic(s, img, xx, 3.95, 0.5, 0.5, crop=False)
        d.tb(s, xx + 0.6, 3.95, 2.2, 0.5, cap, size=11, anchor='m')
    # 8 What we built
    s = d.slide('CONTENT', 'What We Built (and Didn’t)', notes="1:50–2:05. Built, all live in the GitHub repo: the 3D model, photoreal Cycles renders, the installable app, the website with a working waitlist, the promo film, and a technical design + parts list (~$247 per prototype). Not yet: a hardware prototype, FCC/carrier certification, a custom PCB. Cut on purpose: accounts and logins, app-store release, maps up close: none of them test our two bets.")
    d.box(s, 0.75, 1.3, 5.6, 0.32, fill=TEAL, line=None, radius=0.3); d.tb(s, 0.9, 1.3, 5.4, 0.32, 'BUILT', size=10, bold=True, color=WHITE, anchor='m')
    d.box(s, 6.55, 1.3, 2.7, 0.32, fill=ORANGE, line=None, radius=0.3); d.tb(s, 6.7, 1.3, 2.5, 0.32, 'NOT YET', size=10, bold=True, color=WHITE, anchor='m')
    built = [(c['mockup'], '3D model'), (c['hero'], 'Cycles renders'), (c['app'][0], 'App (PWA)'), (c['sitedemo_poster'], 'Site + waitlist'), (c['film_poster'], 'Promo film')]
    for i, (img, cap) in enumerate(built):
        xx = 0.75 + i * 1.13; ph = cap == 'App (PWA)'
        d.box(s, xx, 1.75, 1.03, 1.03, fill=WHITE, line=INK, radius=0.08)
        if ph: d.pic(s, img, xx + 0.28, 1.79, 0.47, 0.95, focus=(0.5, 0.15))
        else: d.pic(s, img, xx + 0.04, 1.79, 0.95, 0.95, focus=(0.5, 0.5))
        d.tb(s, xx - 0.05, 2.83, 1.13, 0.3, cap, size=9, align='c')
    for i, (img, cap) in enumerate([(TPL + '/s9_135.png', 'Hardware prototype'), (TPL + '/s9_137.png', 'FCC + carrier'), (TPL + '/s9_139.png', 'Custom PCB')]):
        xx = 6.6 + i * 0.9; d.pic(s, img, xx + 0.08, 1.8, 0.7, 0.7, crop=False); d.tb(s, xx - 0.1, 2.55, 1.05, 0.45, cap, size=9, align='c')
    d.box(s, 0.75, 3.3, 8.5, 1.45, fill=PEACH, line=None, radius=0.06)
    d.tb(s, 1.0, 3.38, 8.1, 1.3, '', lines=[('STACK', dict(size=9, bold=True, color=CORAL)),
        ('Claude Code (agents) · three.js · Blender Cycles · HTML/JS PWA + Web Bluetooth · Google Forms · GitHub Pages · Playwright + ffmpeg', dict(size=11)),
        ('CUT ON PURPOSE', dict(size=9, bold=True, color=CORAL)), (c['cut'], dict(size=11))], spacing=3)
    # 9 Film
    s = d.slide('CONTENT', 'The Film', notes=f"2:05–2:35. Click the video to play the 28-second cut (the full 68-second film is at {c['film_full']}). Say nothing over it.")
    d.movie(s, c['film'], c['film_poster'], 1.55, 1.25, 6.9, 3.88)
    # 10 App demo
    s = d.slide('CONTENT', 'Live Demo: the App', notes=f"2:35–3:15. Live: open {c['app_url']} on a phone (or this laptop). Flow: start the night → simulate a friend drifting away → find a friend (distance counts down) → I'm home → SOS from the {W_}. If the live demo fails, click the recording on the right.")
    steps = [('Start the night', 'Create the group'), ('Drift + find', 'Separation alert, distance to the metre'), ('Home + SOS', 'From the ' + W_ + ', no phone needed')]
    for i, (h, sub) in enumerate(steps):
        y = 1.4 + i * 0.85; d.circ(s, 0.75, y, 0.55, INK if i else CORAL, f'0{i+1}', 12)
        d.tb(s, 1.42, y - 0.02, 2.3, 0.3, h, size=13.5, bold=True); d.tb(s, 1.42, y + 0.27, 2.3, 0.35, sub, size=9.5, color=GREY)
    d.qr(s, c['app_url'], 0.8, 3.95, 0.82); d.tb(s, 1.7, 4.0, 2.3, 0.7, '', lines=[('Try it on your phone', dict(size=10, bold=True)), (c['app_url'].replace('https://', ''), dict(size=8, color=CORAL))])
    d.movie(s, c['appdemo'], c['appdemo_poster'], 3.95, 1.3, 5.3, 2.98)
    d.tb(s, 3.95, 4.32, 5.3, 0.4, 'Recording of the app (click to play), backup for the live demo', size=9, color=GREY, align='c')
    # 11 Website + waitlist test
    s = d.slide('CONTENT', 'Live Demo: Website + Waitlist Test', notes=f"3:15–3:40. Show {c['site_url']}: scroll to the buttons, the app, range, design. Then the waitlist test: type a test name, submit, and show the confirmation. The recording submits 'Test - Sprint 2 demo' (intercepted, so it didn't add a row). Live, submit a test entry and show it arriving in the Firefly waitlist Google Form responses. Say the real number of sign-ups so far.")
    d.movie(s, c['sitedemo'], c['sitedemo_poster'], 0.75, 1.3, 5.6, 3.15)
    d.tb(s, 0.75, 4.5, 5.6, 0.3, 'Recording: scroll the site, then submit a test sign-up (click to play)', size=9, color=GREY, align='c')
    d.box(s, 6.6, 1.3, 2.65, 1.55, fill=PEACH, line=None, radius=0.08)
    d.tb(s, 6.75, 1.38, 2.4, 1.4, '', lines=[('WAITLIST = DEMAND TEST', dict(size=9, bold=True, color=CORAL)), ('[ N ] sign-ups', dict(size=24, bold=True)), ('Same Google Form for every version: name, email, how often they go out, what matters most', dict(size=9, color=GREY))], spacing=2)
    d.qr(s, c['site_url'], 6.6, 3.05, 0.95); d.tb(s, 7.65, 3.1, 1.65, 0.9, '', lines=[('Open the site', dict(size=10, bold=True)), (c['site_url'].replace('https://', ''), dict(size=8, color=CORAL))])
    # 12 Process
    s = d.slide('CONTENT', 'Process: Three Designs, One Product', notes="3:40–3:55. We iterated the form factor three times with agents doing the rebuilds (3D model, renders, app, site, film each time). Biggest technical challenge: 6-mile range with no phone. A wrist radio can't do it, so we added LTE-M cellular with Sidewalk as a fallback, and re-did the battery and weight budgets each time.")
    for i, (img, cap) in enumerate(c['process']):
        xx = 0.75 + i * 2.95
        p = img if os.path.exists(img) else c['hero']
        d.box(s, xx, 1.3, 2.4, 1.6, fill=PEACH, line=None, radius=0.06); d.pic(s, p, xx + 0.08, 1.36, 2.24, 1.48, focus=(0.5, 0.5))
        d.tb(s, xx, 2.95, 2.4, 0.3, cap, size=10.5, bold=(i == 2), align='c', color=CORAL if i == 2 else INK)
        if i < 2: d.box(s, xx + 2.45, 1.95, 0.45, 0.3, fill=INK, line=None, shape=MSO_SHAPE.RIGHT_ARROW)
    for i, (h, body, col) in enumerate([('DECISION', c['decision'], TEAL), ('BIGGEST CHALLENGE', '6 miles with a dead phone. Fix: LTE-M cellular + Sidewalk, new battery and weight budgets.', ORANGE), ('CUT', c['cut'], CORAL)]):
        xx = 0.75 + i * 2.88; d.box(s, xx, 3.4, 2.74, 1.35, fill=WHITE, line=INK, radius=0.06)
        d.tb(s, xx + 0.12, 3.47, 2.5, 1.25, '', lines=[(h, dict(size=9, bold=True, color=col)), (body, dict(size=10))], spacing=2)
    # 13 Validation
    s = d.slide('CONTENT', '10 People Tried It', notes="3:55–4:20. FILL IN before presenting: the numbers come from the Firefly_User_Test dashboard (Export CSV). Colour one person orange per tester who passed (replace the grey icon with the orange one from the template). Read ONE quote; all ten are in the appendix. Our bar was 8/10 for H1 and H2.")
    rows = [('H1', 'found the hidden friend, no hints, ≤ 120 s'), ('H2', 'pressed I’m home first, unprompted'), ('', 'would wear it on a night out')]
    for r, (h, lab) in enumerate(rows):
        y = 1.38 + r * 0.72
        for k in range(10): d.pic(s, TPL + '/s11_175.png', 0.75 + k * 0.29, y, 0.25, 0.38, crop=False)
        d.tb(s, 3.75, y - 0.04, 1.2, 0.45, '[ _ /10]', size=20, bold=True, color=CORAL)
        d.tb(s, 4.95, y - 0.02, 4.3, 0.45, (h + ' · ' if h else '') + lab + ('  (bar: 8/10)' if h else ''), size=11, anchor='m')
    d.box(s, 0.75, 3.62, 4.15, 1.12, fill=WHITE, line=INK, radius=0.06)
    d.tb(s, 0.9, 3.66, 3.9, 1.05, '', lines=[('HOW WE TESTED', dict(size=9, bold=True, color=TEAL)), ('Task 1: lost in a club, phone dead. Find the friend using only the pulses.', dict(size=9.5)), ('Task 2: the night is over. What do you press?', dict(size=9.5)), ('Then a 3-question survey + one direct quote.', dict(size=9.5, color=GREY))], spacing=1)
    d.box(s, 5.1, 3.62, 4.15, 1.12, fill=PEACH, line=None, radius=0.06)
    d.tb(s, 5.25, 3.7, 3.9, 1.0, '', lines=[('“[Strongest tester quote]”', dict(size=14, italic=True)), ('Tester, [age, how often they go out]', dict(size=9, color=GREY))], spacing=4)
    # 14 Learned
    s = d.slide('CONTENT', 'What We Learned', notes="4:20–4:35. One line per icon. 'Validated' comes from the test results; fill it in. The other two are from the build itself.")
    for i, (img, h, body, col) in enumerate([(TPL + '/s12_213.png', 'Validated', '[from the 10 tests: which bet held up]', TEAL), (TPL + '/s12_217.png', 'Surprised us', c['surprise'], ORANGE), (TPL + '/s12_221.png', 'Would redo', c['redo'], CORAL)]):
        xx = 0.8 + i * 2.9; d.circ(s, xx + 0.7, 1.45, 1.2, col); d.pic(s, img, xx + 1.0, 1.75, 0.6, 0.6, crop=False)
        d.tb(s, xx, 2.85, 2.6, 0.4, h, size=15, bold=True, align='c'); d.tb(s, xx, 3.3, 2.6, 1.4, body, size=11, color=GREY, align='c')
    # 15 Next
    s = d.slide('CONTENT', 'What’s Next', notes=f"4:35–4:52. Top three next steps. Biggest risk: {c['risk']} Go-to-market: start with friend groups that already go out together (club teams, Greek life, roommates), price $149–199 with no monthly fee (data bundled), convert the waitlist into pre-orders. Reorder the steps if testers asked for something else.")
    d.pic(s, TPL + '/s13_230.png', 0.75, 1.3, 8.5, 2.8, crop=False)
    for i, (h, sub) in enumerate(c['next']):
        xx = 0.95 + i * 2.75; d.tb(s, xx, 4.12, 2.6, 0.35, h, size=13, bold=True, align='c'); d.tb(s, xx, 4.44, 2.6, 0.3, sub, size=9, color=CORAL, align='c')
    d.tb(s, 0.75, 4.86, 8.5, 0.25, 'Biggest risk: ' + c['risk'] + '   ·   GTM: friend groups first, $149–199, no monthly fee', size=8.5, color=GREY, align='c')
    # 16 Close
    s = d.slide('STATEMENT', notes="4:52–5:00. Close the loop with the opening story: same night, everyone accounted for. End on the image, then stop.")
    d.tb(s, 0.75, 0.95, 4.6, 0.9, '2:47 AM', size=48); d.tb(s, 4.6, 1.15, 4.6, 0.6, 'Everyone’s home.', size=24, italic=True, color=CORAL)
    d.pic(s, TPL + '/s14_245.png', 0.75, 2.1, 8.5, 3.0, crop=False)
    # 17 Appendix quotes
    s = d.slide('CONTENT', 'Appendix: 10 Tester Quotes', notes="Not presented. The rubric requires 10 direct user quotes: paste them from the user-test CSV (directQuote column).")
    for i in range(10):
        xx = 0.75 + (i % 2) * 4.4; y = 1.4 + (i // 2) * 0.66
        d.box(s, xx, y, 4.1, 0.56, fill=WHITE, line=INK, radius=0.1); d.tb(s, xx + 0.15, y, 3.8, 0.56, f'“[Quote {i+1}]”  Tester {i+1}', size=10, anchor='m')
    # 18 Appendix feasibility
    s = d.slide('CONTENT', 'Appendix: Is It Buildable?', notes="For Q&A. Full numbers and sources: technical/TECHNICAL_DESIGN.md in the repo.")
    for i, (k, v) in enumerate(c['feas']):
        y = 1.35 + i * 0.56; d.box(s, 0.75, y, 8.5, 0.48, fill=WHITE if i % 2 else PEACH, line=None, radius=0.2)
        d.tb(s, 0.95, y, 2.6, 0.48, k, size=11, bold=True, anchor='m'); d.tb(s, 3.55, y, 5.6, 0.48, v, size=11, anchor='m')
    return d.finish()

if __name__ == '__main__':
    print(build(sys.argv[1]))
