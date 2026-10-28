import asyncio, base64, sys
from playwright.async_api import async_playwright
S='/tmp/claude-0/-home-claude/05671788-1db4-51ad-86c7-0131427b2680/scratchpad/v2'
O='/tmp/claude-0/-home-claude/05671788-1db4-51ad-86c7-0131427b2680/scratchpad/v2b_video/frames/'
TEST = len(sys.argv)>1 and sys.argv[1]=='test'
W,H=1920,1080
CLOSE=(0.35,0.66,92,(0,2.5,0))
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(args=['--use-gl=angle','--use-angle=swiftshader'])
        pg=await (await b.new_context(viewport={'width':1400,'height':900})).new_page()
        errs=[]; pg.on('pageerror',lambda e: errs.append(str(e)))
        await pg.goto('file://'+S+'/mockup/test.html'); await pg.wait_for_timeout(2500)
        async def setup(view,state,finish='gold',fov=19):
            await pg.evaluate(f"""(()=>{{ FW.photo(true,0x140e10); FW.stone(0x1c1315); FW.glow(1.9); FW.finish('{finish}'); FW.state('{state}'); FW.xray(false); FW.explode(0); FW.wrist(false); FW.fov({fov}); FW.view({view[0]},{view[1]},{view[2]},[{view[3][0]},{view[3][1]},{view[3][2]}]); }})()""")
        async def grab(name,t):
            d=await pg.evaluate(f"FW.render({t},{W},{H})"); open(O+f'{name}.png','wb').write(base64.b64decode(d.split(',')[1]))
        seqs=[('find',CLOSE,'find','gold',3.0,72),('come',CLOSE,'come','gold',0.0,58),('home',CLOSE,'home','silver',0.0,48),('sos',CLOSE,'sos','black',1.5,72),('apart',CLOSE,'apart','rose',0.0,54)]
        for name,view,state,fin,t0,n in seqs:
            await setup(view,state,fin)
            for i in range(1 if TEST else n): await grab(f'{name}_{i:03d}', t0+i/24 + (1.0 if TEST else 0))
            print(name,flush=True)
        await setup((0.0,1.02,205,(0,-15,0)),'idle','gold',16)
        for i in range(1 if TEST else 96):
            await pg.evaluate(f"FW.view({0.55+i/96*6.2832},1.02,205,[0,-15,0])"); await grab(f'turn_{i:03d}',0)
        print('turn errors',errs); await b.close()
asyncio.run(main())
