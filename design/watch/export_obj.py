import asyncio, base64, json
from playwright.async_api import async_playwright
S='/tmp/claude-0/-home-claude/05671788-1db4-51ad-86c7-0131427b2680/scratchpad/watch/'
JS=r"""(()=>{ const T=FW.THREE; FW.explode(0); FW.photo(false); FW.time(10,9,36); FW.state('idle'); FW.xray(false); FW.render(0,64,64);
  const out=[], mtl=new Set(); let vo=1, to=1, no=1; const v=new T.Vector3(), n=new T.Vector3(), M=new T.Matrix4(), NM=new T.Matrix3(), IM=new T.Matrix4();
  const visible=o=>{ for(let p=o;p;p=p.parent){ if(!p.visible) return false; } return true; };
  let k=0;
  FW.scene.updateMatrixWorld(true);
  FW.scene.traverse(o=>{ if(!o.isMesh) return; const name=(o.material&&o.material.name)||''; const isGlow=name.startsWith('glow_');
    if(!name) return; if(!isGlow && !visible(o)) return;
    const g=o.geometry, P=g.attributes.position, N=g.attributes.normal, U=g.attributes.uv; const idx=g.index;
    const count=o.isInstancedMesh?o.count:1;
    for(let c=0;c<count;c++){
      M.copy(o.matrixWorld); if(o.isInstancedMesh){ o.getMatrixAt(c,IM); M.multiply(IM); } NM.getNormalMatrix(M);
      out.push(`o ${name}_${k++}`); out.push(`usemtl ${name}`); mtl.add(name);
      for(let i=0;i<P.count;i++){ v.fromBufferAttribute(P,i).applyMatrix4(M); out.push(`v ${v.x.toFixed(4)} ${v.y.toFixed(4)} ${v.z.toFixed(4)}`); }
      if(N) for(let i=0;i<N.count;i++){ n.fromBufferAttribute(N,i).applyMatrix3(NM).normalize(); out.push(`vn ${n.x.toFixed(4)} ${n.y.toFixed(4)} ${n.z.toFixed(4)}`); }
      if(U) for(let i=0;i<U.count;i++){ out.push(`vt ${U.getX(i).toFixed(5)} ${U.getY(i).toFixed(5)}`); }
      const tri=idx?idx.count/3:P.count/3; const det=M.determinant();
      for(let t=0;t<tri;t++){ let a=idx?idx.getX(3*t):3*t, b=idx?idx.getX(3*t+1):3*t+1, cc=idx?idx.getX(3*t+2):3*t+2; if(det<0){ const tmp=b; b=cc; cc=tmp; }
        const f=x=>`${x+vo}/${U?x+to:''}/${N?x+no:''}`; out.push(`f ${f(a)} ${f(b)} ${f(cc)}`); }
      vo+=P.count; if(U) to+=U.count; if(N) no+=N.count; }
  });
  return JSON.stringify({obj:out.join('\n'), mtl:[...mtl]});
})()"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=["--use-gl=swiftshader","--enable-webgl","--ignore-gpu-blocklist"])
        pg = await (await b.new_context(viewport={'width':800,'height':600})).new_page()
        await pg.goto('file://'+S+'test.html'); await pg.wait_for_timeout(2500)
        d=json.loads(await pg.evaluate(JS))
        open(S+'blender/watch.obj','w').write('mtllib watch.mtl\n'+d['obj'])
        open(S+'blender/watch.mtl','w').write('\n'.join(f'newmtl {m}\nKd 0.8 0.8 0.8\n' for m in d['mtl']))
        png=await pg.evaluate("FW.dialPNG()"); open(S+'blender/dial.png','wb').write(base64.b64decode(png.split(',')[1]))
        print('materials', d['mtl'], 'lines', d['obj'].count('\n'))
        await b.close()
asyncio.run(main())
