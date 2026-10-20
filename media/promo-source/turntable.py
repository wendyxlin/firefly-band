import asyncio, math, base64, sys, time
from playwright.async_api import async_playwright
LIMIT = int(sys.argv[1]) if len(sys.argv) > 1 else 10**9
OUT = '/tmp/claude-0/-home-claude/05671788-1db4-51ad-86c7-0131427b2680/scratchpad/promo/frames3d/'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=["--use-gl=swiftshader","--enable-webgl","--ignore-gpu-blocklist"])
        ctx = await b.new_context(viewport={'width':1280,'height':800}, color_scheme='dark')
        pg = await ctx.new_page()
        await pg.goto('file:///tmp/claude-0/-home-claude/05671788-1db4-51ad-86c7-0131427b2680/scratchpad/test.html')
        await pg.wait_for_timeout(1500)
        await pg.evaluate("FF3D.spin(false); FF3D.wrist(false); FF3D.grid(false); FF3D.finish('champagne'); window.__ffPaused=true")
        n=[0]
        async def shot(name, t, js=''):
            if n[0] >= LIMIT: return
            data = await pg.evaluate(f"(()=>{{ {js}; return FF3D.renderFrame({t},1920,1080); }})()")
            open(OUT+name+'.png','wb').write(base64.b64decode(data.split(',')[1])); n[0]+=1
        t0=time.time()
        for i in range(96):
            th = 0.6 + i/96*2*math.pi
            await shot(f'turn_{i:03d}', i/24, f"FF3D.view({th},1.12,150); FF3D.target(0,30,0)")
        print('turn', time.time()-t0, flush=True)
        for i in range(48):
            e = (1-math.cos(math.pi*i/47))/2
            await shot(f'expl_{i:03d}', i/24, f"FF3D.view(0.75,1.08,205); FF3D.target(0,50,0); FF3D.explode({e})")
        print('expl', time.time()-t0, flush=True)
        for i in range(24):
            await shot(f'sos_{i:03d}', i/12, "FF3D.explode(0); SIM.state.alert='sos'; SIM.state.finding=false; FF3D.view(0.3,1.0,95); FF3D.target(0,50,0)")
        for i in range(32):
            await shot(f'find_{i:03d}', i/12, f"SIM.state.alert=null; SIM.state.finding=true; SIM.state.leds={1+i*4//32}; FF3D.view(-0.2,0.85,95); FF3D.target(0,50,0)")
        print('done', time.time()-t0, flush=True)
        await b.close()
asyncio.run(main())
