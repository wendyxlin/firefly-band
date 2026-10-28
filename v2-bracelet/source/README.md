# How the v2 bracelet renders and film are made

The scripts were run in a scratch folder, so they contain absolute paths. Before running them, change the path at the top of each file.

## Photo renders (Blender Cycles)

1. `export_obj.py` opens the 3D design review (`mockup/`) in headless Chromium with Playwright. It exports the swept bracelet surface, the buttons and the light to `bracelet.obj`.
2. `blender/render_bracelet.py` builds the studio scene and renders one shot:
   - Principled materials: polished gold, silver, rose gold and black PVD, engraved marks, a ceramic underside and an emissive LED halo
   - Disk and ellipse area lights
   - AgX view transform, depth of field and OpenImageDenoise

   ```
   pip install bpy==5.2.*      # Blender as a Python module (Python 3.13)
   python blender/render_bracelet.py hero 1500 1000 64
   ```

   Shots: `hero`, `buttons`, `find`, `home`, `sos`, `rose`, `silver`, `black`. Each takes about 4–6 minutes on a CPU.

## Film (68 s, 1080p)

1. `video/frames.py` renders the light loops from the three.js model. The loops are find, come find me, home, SOS and separated, plus a turntable.
2. `video/music.py` synthesizes the soundtrack with numpy. It adds buzz cues for separation, find and come find me, and chimes for I'm home.
3. `video/promo.html` draws every scene on a canvas from `renderAt(t)`. It uses the Cycles stills, a crop from the design board, and the fonts in `fonts/`: Cormorant Garamond, DM Sans and JetBrains Mono, all under the SIL Open Font License.
4. `video/capture.py` steps through the timeline at 24 fps and pipes the frames to ffmpeg.
