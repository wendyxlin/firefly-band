# Watch direction (design in review)

A proposal to make Firefly look like a dress watch. It isn't applied to the concept page, website, video or app yet.

- Interactive page with 3D model, range plan and renders: [`docs/watch/index.html`](../../docs/watch/index.html), and on GitHub Pages at `/firefly-band/watch/` once Pages is on
- Feasibility check: [`FEASIBILITY.md`](FEASIBILITY.md)
- `export_obj.py`: exports the 3D model from the page to OBJ (Playwright)
- `blender_render.py`: the Blender Cycles scene behind the photo-style renders (`python blender_render.py hero 1500 1000 64`, with `bpy` 5.2 installed and `watch.obj` and `dial.png` alongside)
