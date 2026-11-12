import subprocess, os
R={'reel1-u-home':[('r1a',.8,0),('r1b',.7,0),('r1c',1.4,0),('r1d',2.6,1),('r1e',2.8,1),('r1f',2.8,1)],
   'reel2-three-reasons':[('r2a',2.2,1),('r2b',2.6,1),('r2c',2.6,1),('r2d',2.6,1),('r2e',2.8,1)],
   'reel3-pick-your-shade':[('r3a',1.3,1),('r3b',1.1,1),('r3c',1.1,1),('r3d',1.1,1),('r3e',2.8,0)],
   'reel4-phone-died':[('r4a',1.8,0),('r4b',1.6,0),('r4c',2.8,1),('r4d',2.6,1),('r4e',2.8,1)]}
ENC=['-c:v','libx264','-crf','18','-preset','veryfast','-pix_fmt','yuv420p','-r','30']
os.makedirs('seg',exist_ok=True); os.makedirs('final',exist_ok=True)
for name,scenes in R.items():
    lst=[]
    for f,d,zoom in scenes:
        n=round(d*30); out=f'seg/{f}.mp4'; tmp=f'seg/{f}.tmp.mp4'
        if zoom: vf=f"scale=2160:3840,zoompan=z='1+0.045*on/{n}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={n}:s=1080x1920:fps=30,format=yuv420p"
        else: vf=f"format=yuv420p,loop=-1:1,trim=duration={n/30}"
        cmd=['ffmpeg','-y','-loglevel','error']+(['-i',f'out/{f}.png'] if zoom else ['-framerate','30','-i',f'out/{f}.png'])+['-vf',vf,'-frames:v',str(n)]+ENC+[tmp]
        subprocess.run(cmd,check=True); os.replace(tmp,out); lst.append(f"file '{os.path.abspath(out)}'")
    open('list.txt','w').write('\n'.join(lst))
    tot=sum(d for _,d,_ in scenes)
    subprocess.run(['ffmpeg','-y','-loglevel','error','-f','concat','-safe','0','-i','list.txt','-f','lavfi','-t',str(tot),'-i','anullsrc=r=44100:cl=stereo','-map','0:v','-map','1:a','-c:v','copy','-c:a','aac','-b:a','96k','-shortest','-movflags','+faststart',f'final/{name}.tmp.mp4'],check=True)
    os.replace(f'final/{name}.tmp.mp4',f'final/{name}.mp4')
    print(name,tot,os.path.getsize(f'final/{name}.mp4')//1024,'KB')
