import asyncio, base64, sys, os
from playwright.async_api import async_playwright
S='/tmp/claude-0/-home-claude/05671788-1db4-51ad-86c7-0131427b2680/scratchpad/v2'
TEST = len(sys.argv)>1 and sys.argv[1]=='test'
W,H=1920,1080
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(args=['--use-gl=angle','--use-angle=swiftshader','--allow-file-access-from-files'])
        pg=await (await b.new_context(viewport={'width':1400,'height':900})).new_page()
        errs=[]; pg.on('pageerror',lambda e: errs.append(str(e)))
        await pg.goto('file://'+S+'/mockup/test.html'); await pg.wait_for_timeout(2500)
        async def setup(view, state, finish='yellow', strap='black', tone=0x15111c, stone=0x241c2e, fov=19, exposure=None):
            await pg.evaluate(f"""(()=>{{ FW.photo(true,{tone}); FW.stone({stone}); FW.finish('{finish}'); FW.strap('{strap}'); FW.state('{state}'); FW.xray(false); FW.explode(0); FW.time(10,9,0); FW.fov({fov}); FW.view({view[0]},{view[1]},{view[2]},[{view[3][0]},{view[3][1]},{view[3][2]}]); {'FW.exposure(%s);'%exposure if exposure else ''} }})()""")
        async def grab(name,t):
            d=await pg.evaluate(f"FW.render({t},{W},{H})")
            open(f'frames/{name}.png','wb').write(base64.b64decode(d.split(',')[1]))
        seqs=[ # name, view, state, finish, strap, period(s)
            ('apart',(1.5708+0.25,0.55,140,(0,7,0)),'apart','yellow','black',3.14159/2.6),
            ('home', (1.5708-0.2,0.5,140,(0,7,0)),'home','yellow','plum',1/0.9),
            ('sos',  (1.5708-0.3,0.6,140,(0,7,0)),'sos','steel','black',3.14159/6),
        ]
        for name,view,state,fin,strap,per in seqs:
            await setup(view,state,fin,strap)
            n=1 if TEST else max(1,round(per*24))
            for i in range(n): await grab(f'{name}_{i:03d}', i/24 if not TEST else per*0.3)
            print(name,n,flush=True)
        # turntable: idle, rose/plum, 96 frames over a full turn
        await setup((0.0,1.1,190,(0,-6,0)),'idle','rose','plum',fov=16)
        n=1 if TEST else 96
        for i in range(n):
            await pg.evaluate(f"FW.view({0.9+i/96*6.2832},1.1,190,[0,-6,0])"); await grab(f'turn_{i:03d}',0)
        print('turn',n,'errors',errs); await b.close()
asyncio.run(main())
