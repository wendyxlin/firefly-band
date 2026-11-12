import asyncio, sys, os
sys.argv=['record.py','bracelet','site']
exec(open('/tmp/claude-0/-home-claude/05671788-1db4-51ad-86c7-0131427b2680/scratchpad/deck/record.py').read().split('async def smooth_to')[0])
HERE=os.path.dirname(os.path.abspath(__file__)); os.makedirs(HERE+'/out',exist_ok=True)
async def go():
    async with async_playwright() as p:
        b=await p.chromium.launch(); ctx=await b.new_context(viewport={'width':1080,'height':1920})
        await ctx.route('https://fonts.googleapis.com/**', lambda r: r.fulfill(status=200, content_type='text/css', body=CSS))
        await ctx.route('https://fonts.gstatic.com/**', lambda r: r.fulfill(status=404, body=''))
        pg=await ctx.new_page(); await pg.goto('file://'+HERE+'/reels.html'); ids=await pg.evaluate('IDS')
        for i in ids:
            await pg.goto('file://'+HERE+'/reels.html#'+i); await pg.reload(); await pg.wait_for_timeout(400)
            await pg.evaluate('document.fonts.ready')
            el=await pg.query_selector('.f'); await el.screenshot(path=f'{HERE}/out/{i}.png')
        await b.close(); print(ids)
asyncio.run(go())
