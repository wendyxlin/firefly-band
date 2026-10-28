# How the v2 renders and film are made

The scripts were run in a scratch folder, so they contain absolute paths. Before running them, change the path at the top of each file.

## Photo renders (Blender Cycles)

1. `export_obj.py` opens the 3D design review (`mockup/`) in headless Chromium with Playwright. It exports the three.js watch to `watch.obj` and `watch.mtl`, and the dial texture to `dial.png`.
2. `blender/render.py` builds the studio scene. It uses Principled materials: gold, sapphire, a mother-of-pearl dial with thin-film iridescence, grained leather and stone. It also sets up disk and ellipse area lights, the AgX view transform, depth of field and OpenImageDenoise. It renders one shot:

   ```
   pip install bpy==5.2.*      # Blender as a Python module (Python 3.13)
   python blender/render.py hero 1500 1000 64
   ```

   Shots: `hero`, `buttons`, `apart`, `home`, `sos`, `rose`. Each one takes about 5 minutes on a CPU.

## Film (68 s, 1080p)

1. `video/frames.py` renders the animated dial loops and the turntable from the three.js model. The dial loops are lavender for apart, a green sweep for home and a red pulse for SOS. Output goes to `frames/`.
2. `video/music.py` synthesizes the soundtrack with numpy and writes `music.wav`. Chimes land when the circle receives I'm Home, and buzzes on the separation and SOS beats.
3. `video/promo.html` draws every scene on a canvas from `renderAt(t)`. It uses the Blender stills in `stills/` and the fonts in `fonts/`: Bodoni Moda, Instrument Sans and JetBrains Mono, all under the SIL Open Font License.
4. `video/capture.py` steps through the timeline at 24 fps and pipes the frames to ffmpeg, which writes `afterglow-promo.mp4`. Pass times in seconds to save single stills instead, for example `python capture.py 13 31.5`.
