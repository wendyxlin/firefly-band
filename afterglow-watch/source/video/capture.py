import asyncio, base64, subprocess, sys
from playwright.async_api import async_playwright
FPS=24
STILLS = [float(x) for x in sys.argv[1:]]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=["--allow-file-access-from-files"])
        pg = await (await b.new_context(viewport={'width':1920,'height':1080})).new_page()
        errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('file:///tmp/claude-0/-home-claude/05671788-1db4-51ad-86c7-0131427b2680/scratchpad/v2/video/promo.html')
        await pg.evaluate('window.ready')
        if STILLS:
            for t in STILLS:
                d = await pg.evaluate(f"(renderAt({t}), document.getElementById('c').toDataURL('image/jpeg',0.9))")
                open(f'still_{t:05.1f}.jpg','wb').write(base64.b64decode(d.split(',')[1]))
            print('errors', errs); await b.close(); return
        dur = await pg.evaluate('DUR'); n=int(dur*FPS)
        ff = subprocess.Popen(['ffmpeg','-y','-loglevel','error','-f','image2pipe','-framerate',str(FPS),'-vcodec','mjpeg','-i','-','-i','music.wav',
            '-c:v','libx264','-preset','medium','-crf','19','-pix_fmt','yuv420p','-c:a','aac','-b:a','192k','-shortest','-movflags','+faststart','afterglow-promo.mp4'], stdin=subprocess.PIPE)
        for i in range(n):
            d = await pg.evaluate(f"(renderAt({i/FPS}), document.getElementById('c').toDataURL('image/jpeg',0.93))")
            ff.stdin.write(base64.b64decode(d.split(',')[1]))
            if i % 120 == 0: print('frame', i, '/', n, flush=True)
        ff.stdin.close(); ff.wait(); print('errors', errs, 'ffmpeg', ff.returncode)
        await b.close()
asyncio.run(main())
