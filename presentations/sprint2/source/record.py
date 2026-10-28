"""Screen recordings for the Sprint 2 decks: website + waitlist test, and the app demo, for each design.
Usage: python record.py watch|bracelet site|app
The waitlist POST is intercepted (answered locally), so the recording never adds a row to the real Google Form."""
import asyncio, base64, glob, os, shutil, subprocess, sys
from playwright.async_api import async_playwright
SC = '/tmp/claude-0/-home-claude/05671788-1db4-51ad-86c7-0131427b2680/scratchpad'
OUT = SC + '/deck/rec'
design, what = sys.argv[1], sys.argv[2]
ROOT = {'watch': SC + '/aw/v2-bracelet', 'bracelet': SC + '/v2/site'}[design]
APP = {'watch': SC + '/aw/v2-bracelet/app/index.html', 'bracelet': SC + '/v2/app/index.html'}[design]
F1 = SC + '/v2/video/fontpkgs'; F2 = SC + '/v2b_video/fontpkgs'
def ff(fam, path, w, style='normal'):
    p = glob.glob(path)[0]; b = base64.b64encode(open(p, 'rb').read()).decode()
    return f"@font-face{{font-family:'{fam}';font-style:{style};font-weight:{w};src:url(data:font/woff2;base64,{b}) format('woff2')}}"
CSS = '\n'.join([
    ff('Bodoni Moda', F1 + '/x_*bodoni*/package/files/bodoni-moda-latin-500-normal.woff2', 500),
    ff('Bodoni Moda', F1 + '/x_*bodoni*/package/files/bodoni-moda-latin-600-normal.woff2', 600),
    ff('Bodoni Moda', F1 + '/x_*bodoni*/package/files/bodoni-moda-latin-500-italic.woff2', 500, 'italic'),
    *[ff('Instrument Sans', F1 + f'/x_*instrument*/package/files/instrument-sans-latin-{w}-normal.woff2', w) for w in (400, 500, 600, 700)],
    ff('JetBrains Mono', F1 + '/x_*jetbrains*/package/files/jetbrains-mono-latin-500-normal.woff2', 500),
    ff('JetBrains Mono', F1 + '/x_*jetbrains*/package/files/jetbrains-mono-latin-400-normal.woff2', 400),
    *[ff('Cormorant Garamond', F2 + f'/x_*cormorant*/package/files/cormorant-garamond-latin-{w}-normal.woff2', w) for w in (500, 600)],
    *[ff('Cormorant Garamond', F2 + f'/x_*cormorant*/package/files/cormorant-garamond-latin-{w}-italic.woff2', w, 'italic') for w in (500, 600)],
    *[ff('DM Sans', F2 + f'/x_*dm-sans*/package/files/dm-sans-latin-{w}-normal.woff2', w) for w in (400, 500, 600, 700)],
])
async def smooth_to(pg, sel_or_y, dur=1.6, offset=-70):
    y = sel_or_y if isinstance(sel_or_y, (int, float)) else await pg.evaluate(f"document.querySelector('{sel_or_y}').getBoundingClientRect().top + scrollY + ({offset})")
    await pg.evaluate("""([y,d])=>new Promise(r=>{ const y0=scrollY, t0=performance.now(); function f(n){ const k=Math.min(1,(n-t0)/d); const e=k<.5?4*k*k*k:1-Math.pow(-2*k+2,3)/2; scrollTo(0,y0+(y-y0)*e); k<1?requestAnimationFrame(f):r(); } requestAnimationFrame(f); })""", [y, dur * 1000])
async def main():
    tmp = OUT + f'/tmp_{design}_{what}'; shutil.rmtree(tmp, ignore_errors=True); os.makedirs(tmp)
    async with async_playwright() as p:
        b = await p.chromium.launch()
        ctx = await b.new_context(viewport={'width': 1280, 'height': 720}, device_scale_factor=1, record_video_dir=tmp, record_video_size={'width': 1280, 'height': 720})
        await ctx.route('https://fonts.googleapis.com/**', lambda r: r.fulfill(status=200, content_type='text/css', body=CSS))
        await ctx.route('https://fonts.gstatic.com/**', lambda r: r.fulfill(status=404, body=''))
        posted = []
        async def form(r):
            posted.append(r.request.post_data or ''); await r.fulfill(status=200, body='ok', headers={'access-control-allow-origin': '*'})
        await ctx.route('https://docs.google.com/forms/**', form)
        pg = await ctx.new_page()
        if what == 'site':
            await pg.goto('file://' + ROOT + '/index.html'); await pg.wait_for_timeout(2600)
            for sel in (['#watch', '#app', '#range', '#design'] if design == 'watch' else ['#bracelet', '#app', '#range', '#design']):
                await smooth_to(pg, sel); await pg.wait_for_timeout(1500)
            await smooth_to(pg, '#waitlist', 1.4, -40); await pg.wait_for_timeout(700)
            await pg.click('#wlName'); await pg.keyboard.type('Test - Sprint 2 demo', delay=45)
            await pg.click('#wlEmail'); await pg.keyboard.type('sprint2.test@example.com', delay=35)
            await pg.select_option('#wlFreq', 'A few times a month'); await pg.wait_for_timeout(400)
            await pg.select_option('#wlWhy', 'Knowing everyone got home'); await pg.wait_for_timeout(500)
            await pg.click('#wlBtn'); await pg.wait_for_timeout(2800)
        else:
            await pg.goto('file://' + APP); await pg.add_style_tag(content='body{zoom:.9}'); await pg.wait_for_timeout(1800)
            async def tap(sel, wait=900):
                await pg.hover(sel); await pg.wait_for_timeout(250); await pg.click(sel); await pg.wait_for_timeout(wait)
            await tap('[data-action=start]', 1200)
            await tap('[data-action=separate]', 2200)
            if design == 'watch':
                await tap('[data-tab=friends]'); await tap('[data-action=find]', 5200)
                await tap('[data-tab=checkins]'); await tap('[data-action=home]', 2000)
                await tap('[data-tab=settings]', 700); await pg.evaluate("document.getElementById('appScroll').scrollTo({top:420,behavior:'smooth'})"); await pg.wait_for_timeout(900)
                await tap('[data-action=w-home]', 1800); await tap('[data-action=w-sos]', 2600); await tap('[data-action=ack]', 1800)
            else:
                await tap('[data-tab=settings]', 700); await pg.evaluate("document.getElementById('appScroll').scrollTo({top:300,behavior:'smooth'})"); await pg.wait_for_timeout(900)
                await tap('[data-action=w-find]', 5600)
                await tap('[data-tab=settings]', 700); await pg.evaluate("document.getElementById('appScroll').scrollTo({top:300,behavior:'smooth'})"); await pg.wait_for_timeout(700)
                await tap('[data-action=w-come]', 900); await tap('[data-tab=home]', 2200)
                await tap('[data-tab=checkins]', 600); await tap('[data-action=home]', 2000)
                await tap('[data-tab=settings]', 700); await pg.evaluate("document.getElementById('appScroll').scrollTo({top:300,behavior:'smooth'})"); await pg.wait_for_timeout(700)
                await tap('[data-action=w-sos]', 2600); await tap('[data-action=ack]', 1800)
        await pg.close(); await ctx.close(); await b.close()
    webm = glob.glob(tmp + '/*.webm')[0]
    mp4 = OUT + f'/{design}-{what}-demo.mp4'
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', webm, '-c:v', 'libx264', '-preset', 'medium', '-crf', '22', '-pix_fmt', 'yuv420p', '-r', '30', '-movflags', '+faststart', '-an', mp4], check=True)
    poster = OUT + f'/{design}-{what}-poster.jpg'
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-sseof', '-1.5', '-i', mp4, '-frames:v', '1', poster], check=True)
    dur = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', mp4], capture_output=True, text=True).stdout.strip()
    print(mp4, dur, 's; form posts intercepted:', len(posted))
    shutil.rmtree(tmp, ignore_errors=True)
asyncio.run(main())
