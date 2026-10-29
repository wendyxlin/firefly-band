"""Convert one of our Sprint 2 .pptx decks into Google Slides API requests.
Usage: python pptx_to_slides.py deck.pptx prefix assets_dir raw_base_url out.json
Writes {"batches": [[requests...], ...], "notes": {slideObjectId: text}, "assets": [files]}.
Pictures are saved into assets_dir (by content hash) and referenced by raw_base_url/<file>; the images must be
public at that URL before the requests are sent."""
import hashlib, json, os, sys
from pptx import Presentation
from pptx.enum.shapes import MSO_SHAPE_TYPE, MSO_SHAPE
from pptx.enum.dml import MSO_FILL
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

src, PFX, ADIR, BASE, OUT = sys.argv[1:6]
os.makedirs(ADIR, exist_ok=True)
EMU = 914400
P = Presentation(src)
VIDEO = {'The Film': 'film-30s', 'Live Demo: the App': 'app-demo', 'Live Demo: Website + Waitlist Test': 'site-demo'}
KIND = 'bracelet' if 'Bracelet' in src else 'watch'
VURL = 'https://github.com/wendyxlin/firefly-band/blob/main/presentations/sprint2/media/{}-{}.mp4'
assets = set()

def rgb(c):
    return {'red': int(c[0:2], 16) / 255, 'green': int(c[2:4], 16) / 255, 'blue': int(c[4:6], 16) / 255}
def size_tf(x, y, w, h):
    return {'size': {'width': {'magnitude': max(int(w), 12700), 'unit': 'EMU'}, 'height': {'magnitude': max(int(h), 12700), 'unit': 'EMU'}},
            'transform': {'scaleX': 1, 'scaleY': 1, 'translateX': int(x), 'translateY': int(y), 'unit': 'EMU'}}
def asset(blob, ext):
    fn = hashlib.sha1(blob).hexdigest()[:16] + '.' + ext
    p = os.path.join(ADIR, fn)
    if not os.path.exists(p): open(p, 'wb').write(blob)
    assets.add(fn); return BASE + '/' + fn

DOTS = asset(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tplimg/layout_dots.png'), 'rb').read(), 'png')

def chrome(sid, layout, R):
    R.append({'updatePageProperties': {'objectId': sid, 'pageProperties': {'pageBackgroundFill': {'solidFill': {'color': {'rgbColor': rgb('F1EEE8')}}}}, 'fields': 'pageBackgroundFill.solidFill.color'}})
    lines = [(0.31, 0, 0, 5.625), (9.69, 0, 0, 5.625), (0, 0.59, 10, 0), (0, 5.28, 10, 0)] + ([(0, 1.15, 10, 0)] if layout == 'CONTENT' else [])
    for i, (x, y, w, h) in enumerate(lines):
        lid = f'{sid}_ln{i}'
        R.append({'createLine': {'objectId': lid, 'lineCategory': 'STRAIGHT', 'elementProperties': {'pageObjectId': sid, **size_tf(x * EMU, y * EMU, w * EMU, h * EMU)}}})
        R.append({'updateLineProperties': {'objectId': lid, 'lineProperties': {'weight': {'magnitude': 0.75, 'unit': 'PT'}, 'lineFill': {'solidFill': {'color': {'rgbColor': rgb('000000')}}}}, 'fields': 'weight,lineFill.solidFill.color'}})
    R.append({'createImage': {'objectId': f'{sid}_dots', 'url': DOTS, 'elementProperties': {'pageObjectId': sid, **size_tf(4.5 * EMU, 0.17 * EMU, 1.0 * EMU, 0.25 * EMU)}}})
    hid = f'{sid}_hdr'
    R.append({'createShape': {'objectId': hid, 'shapeType': 'TEXT_BOX', 'elementProperties': {'pageObjectId': sid, **size_tf(0.70 * EMU, 0.15 * EMU, 2.4 * EMU, 0.3 * EMU)}}})
    R.append({'insertText': {'objectId': hid, 'text': 'BTE CAPSTONE'}})
    R.append({'updateTextStyle': {'objectId': hid, 'textRange': {'type': 'ALL'}, 'style': {'fontFamily': 'Arial', 'bold': True, 'fontSize': {'magnitude': 8, 'unit': 'PT'}, 'foregroundColor': {'opaqueColor': {'rgbColor': rgb('000000')}}}, 'fields': 'fontFamily,bold,fontSize,foregroundColor'}})
    R.append({'updateShapeProperties': {'objectId': hid, 'shapeProperties': {'contentAlignment': 'MIDDLE'}, 'fields': 'contentAlignment'}})

SHAPE = {MSO_SHAPE.ROUNDED_RECTANGLE: 'ROUND_RECTANGLE', MSO_SHAPE.OVAL: 'ELLIPSE', MSO_SHAPE.RIGHT_ARROW: 'RIGHT_ARROW', MSO_SHAPE.RECTANGLE: 'RECTANGLE'}
ALIGN = {PP_ALIGN.CENTER: 'CENTER', PP_ALIGN.RIGHT: 'END', PP_ALIGN.LEFT: 'START', None: 'START'}
ANCHOR = {MSO_ANCHOR.MIDDLE: 'MIDDLE', MSO_ANCHOR.BOTTOM: 'BOTTOM', MSO_ANCHOR.TOP: 'TOP', None: 'TOP'}

def text_requests(oid, tf, R, title=False):
    paras = list(tf.paragraphs)
    full = '\n'.join(''.join(r.text for r in p.runs) for p in paras)
    if not full.strip(): return
    R.append({'insertText': {'objectId': oid, 'text': full}})
    L = len(full.encode('utf-16-le')) // 2
    pos = 0
    for pi, p in enumerate(paras):
        pstart = pos
        for r in p.runs:
            n = len(r.text.encode('utf-16-le')) // 2
            if n:
                f = r.font; st = {'fontFamily': 'Arial'}; fields = ['fontFamily']
                sz = f.size.pt if f.size else (28 if title else 14); st['fontSize'] = {'magnitude': sz, 'unit': 'PT'}; fields.append('fontSize')
                st['bold'] = bool(f.bold); st['italic'] = bool(f.italic); fields += ['bold', 'italic']
                try: col = str(f.color.rgb) if f.color and f.color.type is not None else '000000'
                except Exception: col = '000000'
                st['foregroundColor'] = {'opaqueColor': {'rgbColor': rgb(col)}}; fields.append('foregroundColor')
                R.append({'updateTextStyle': {'objectId': oid, 'textRange': {'type': 'FIXED_RANGE', 'startIndex': pos, 'endIndex': pos + n}, 'style': st, 'fields': ','.join(fields)}})
            pos += n
        pend = pos + (1 if pi < len(paras) - 1 else 0)
        ps = {'alignment': 'CENTER' if title else ALIGN.get(p.alignment, 'START'), 'spaceAbove': {'magnitude': 0, 'unit': 'PT'}, 'spaceBelow': {'magnitude': p.space_after.pt if p.space_after else 0, 'unit': 'PT'}, 'lineSpacing': 100}
        if pstart < L: R.append({'updateParagraphStyle': {'objectId': oid, 'textRange': {'type': 'FIXED_RANGE', 'startIndex': pstart, 'endIndex': min(max(pend, pstart + 1), L)}, 'style': ps, 'fields': 'alignment,spaceAbove,spaceBelow,lineSpacing'}})
        pos += 1  # the newline between paragraphs

slides_out = []; notes = {}
for si, s in enumerate(P.slides, 1):
    sid = f'{PFX}s{si:02d}'; R = []
    R.append({'createSlide': {'objectId': sid, 'insertionIndex': si - 1, 'slideLayoutReference': {'predefinedLayout': 'BLANK'}}})
    chrome(sid, s.slide_layout.name, R)
    title = ''
    shapes = list(s.shapes)
    for k, sh in enumerate(shapes):
        oid = f'{sid}_e{k:02d}'
        x, y, w, h = sh.left or 0, sh.top or 0, sh.width or 0, sh.height or 0
        ep = {'pageObjectId': sid, **size_tf(x, y, w, h)}
        if sh.shape_type == MSO_SHAPE_TYPE.PICTURE:
            url = asset(sh.image.blob, sh.image.ext.replace('jpeg', 'jpg'))
            R.append({'createImage': {'objectId': oid, 'url': url, 'elementProperties': ep}})
            props, fields = {}, []
            try:
                if sh.line.fill.type == MSO_FILL.SOLID:
                    props['outline'] = {'outlineFill': {'solidFill': {'color': {'rgbColor': rgb(str(sh.line.color.rgb))}}}, 'weight': {'magnitude': sh.line.width.pt or 0.75, 'unit': 'PT'}}; fields.append('outline')
            except Exception: pass
            nxt = shapes[k + 1] if k + 1 < len(shapes) else None
            if nxt is not None and nxt.has_text_frame and nxt.text_frame.text.strip() == '▶' and title in VIDEO:
                props['link'] = {'url': VURL.format(KIND, VIDEO[title])}; fields.append('link')
            if fields: R.append({'updateImageProperties': {'objectId': oid, 'imageProperties': props, 'fields': ','.join(fields)}})
            continue
        if sh.is_placeholder:
            title = sh.text_frame.text
            R.append({'createShape': {'objectId': oid, 'shapeType': 'TEXT_BOX', 'elementProperties': ep}})
            text_requests(oid, sh.text_frame, R, title=True); continue
        st = 'TEXT_BOX' if sh.shape_type == MSO_SHAPE_TYPE.TEXT_BOX else SHAPE.get(getattr(sh, 'auto_shape_type', None), 'RECTANGLE')
        R.append({'createShape': {'objectId': oid, 'shapeType': st, 'elementProperties': ep}})
        props, fields = {}, []
        if st != 'TEXT_BOX':
            if sh.fill.type == MSO_FILL.SOLID:
                props['shapeBackgroundFill'] = {'solidFill': {'color': {'rgbColor': rgb(str(sh.fill.fore_color.rgb))}}}
            else:
                props['shapeBackgroundFill'] = {'propertyState': 'NOT_RENDERED'}
            fields.append('shapeBackgroundFill')
            if sh.line.fill.type == MSO_FILL.SOLID:
                props['outline'] = {'outlineFill': {'solidFill': {'color': {'rgbColor': rgb(str(sh.line.color.rgb))}}}, 'weight': {'magnitude': sh.line.width.pt or 0.75, 'unit': 'PT'}}
            else:
                props['outline'] = {'propertyState': 'NOT_RENDERED'}
            fields.append('outline')
        if sh.has_text_frame and sh.text_frame.text.strip():
            props['contentAlignment'] = ANCHOR.get(sh.text_frame.vertical_anchor, 'MIDDLE' if st != 'TEXT_BOX' else 'TOP'); fields.append('contentAlignment')
        if fields: R.append({'updateShapeProperties': {'objectId': oid, 'shapeProperties': props, 'fields': ','.join(fields)}})
        if sh.has_text_frame: text_requests(oid, sh.text_frame, R)
    if s.has_notes_slide: notes[sid] = s.notes_slide.notes_text_frame.text
    slides_out.append(R)

json.dump({'slides': slides_out, 'notes': notes, 'assets': sorted(assets)}, open(OUT, 'w'))
print(OUT, len(slides_out), 'slides', sum(len(r) for r in slides_out), 'requests', len(assets), 'assets')
