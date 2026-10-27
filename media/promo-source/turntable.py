import asyncio, math, base64, sys, time
from playwright.async_api import async_playwright
S='/tmp/claude-0/-home-claude/05671788-1db4-51ad-86c7-0131427b2680/scratchpad/'
OUT = S+'promo/frames_bangle/'
TEST = len(sys.argv)>1 and sys.argv[1]=='test'
TURN=(1.12,196,(0,30,0)); EXPL=(0.75,1.12,330,(0,0,0)); CLOSE=(95,(0,50,0))
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=["--use-gl=swiftshader","--enable-webgl","--ignore-gpu-blocklist"])
        pg = await (await b.new_context(viewport={'width':1280,'height':800}, color_scheme='dark')).new_page()
        errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('file://'+S+'render_promo.html'); await pg.wait_for_timeout(1500)
        await pg.evaluate("FF3D.spin(false); FF3D.wrist(false); FF3D.grid(false); FF3D.coin(false); FF3D.finish('champagne'); window.__ffPaused=true")
        async def shot(name, t, js=''):
            data = await pg.evaluate(f"(()=>{{ {js}; return FF3D.renderFrame({t},1920,1080); }})()")
            open(OUT+name+'.png','wb').write(base64.b64decode(data.split(',')[1]))
        t0=time.time()
        rng = (lambda n: [0, n//2, n-1]) if TEST else (lambda n: range(n))
        for i in rng(96):
            th = 0.6 + i/96*2*math.pi
            await shot(f'turn_{i:03d}', i/24, f"SIM.state.alert=null; SIM.state.finding=false; FF3D.explode(0); FF3D.view({th},{TURN[0]},{TURN[1]}); FF3D.target{TURN[2]}")
        for i in rng(48):
            e = (1-math.cos(math.pi*i/47))/2
            await shot(f'expl_{i:03d}', i/24, f"FF3D.view({EXPL[0]},{EXPL[1]},{260+150*e}); FF3D.target(0,{30-10*e},0); FF3D.explode({e})")
        print('turn+expl', round(time.time()-t0), flush=True)
        for i in rng(24):
            await shot(f'sos_{i:03d}', i/12, f"FF3D.explode(0); SIM.state.alert='sos'; SIM.state.finding=false; FF3D.view(0.3,1.0,{CLOSE[0]}); FF3D.target{CLOSE[1]}")
        for i in rng(32):
            await shot(f'find_{i:03d}', i/12, f"FF3D.explode(0); SIM.state.alert=null; SIM.state.finding=true; SIM.state.leds={1+i*4//32}; FF3D.view(-0.2,0.85,{CLOSE[0]}); FF3D.target{CLOSE[1]}")
        for i in rng(24):
            await shot(f'ok_{i:03d}', i/12, f"FF3D.explode(0); SIM.state.alert='ok'; SIM.state.finding=false; FF3D.view(0.55,0.95,{CLOSE[0]}); FF3D.target{CLOSE[1]}")
        print('done', round(time.time()-t0), 'errors', errs, flush=True)
        await b.close()
asyncio.run(main())
