"""Printable parts for the Firefly bangle (fine-jewelry version), from the same numbers as the page (mm).
Outputs: firefly_centerpiece_base.stl, firefly_centerpiece_dome.stl, firefly_clasp_box.stl
Requires: pip install trimesh manifold3d numpy"""
import numpy as np, trimesh
from trimesh.creation import cylinder, box, torus, icosphere

def rounded_block(l, h, w, r, b):
    """Convex hull of eight corner tori: plan corner radius r, all edges rounded with radius b (X = l, Y = h, Z = w)."""
    pts = []
    for sx in (-1, 1):
        for sz in (-1, 1):
            for sy in (-1, 1):
                t = torus(major_radius=max(r - b, 0.01), minor_radius=b, major_sections=24, minor_sections=12)
                t.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, [1, 0, 0]))
                t.apply_translation([sx * (l / 2 - r), sy * (h / 2 - b), sz * (w / 2 - r)])
                pts.append(t.vertices)
    return trimesh.convex.convex_hull(np.vstack(pts))

M = dict(engine="manifold")
WALL = 1.0
# ---------- centerpiece: 28 x 24 x 11 cushion + 1.9 mm dome ----------
L, H, W, R, B = 28.0, 11.0, 24.0, 7.5, 3.5
outer = rounded_block(L, H, W, R, B)
dome = icosphere(subdivisions=4); dome.apply_scale([11, 1.9, 9]); dome.apply_translation([0, H / 2 - 0.15, 0])
cut = box([30, 4, 30]); cut.apply_translation([0, H / 2 - 0.15 - 2, 0])
dome = dome.difference(cut, **M)                            # keep the upper half of the ellipsoid
body = outer.union(dome, **M)
inner = rounded_block(L - 2 * WALL, H - 2 * WALL, W - 2 * WALL, R - WALL, B - WALL)
shell = body.difference(inner, **M)
# collet seat for the 15 x 11 stone (opening 13.6 x 9.6 leaves a 0.7 mm ledge), bead button holes, band channel
seat = cylinder(radius=1, height=6, sections=96); seat.apply_scale([6.8, 1, 4.8]); seat.apply_translation([0, H / 2 + 1, 0])
shell = shell.difference(seat, **M)
for x in (-10.5, 10.5):
    hole = cylinder(radius=1.0, height=6, sections=32); hole.apply_translation([x, H / 2, 0]); shell = shell.difference(hole, **M)
chan = box([L + 4, 3.4, 6.4]); chan.apply_translation([0, -H / 2, 0]); shell = shell.difference(chan, **M)
# charge-free: split at the parting line
def half(mesh, top):
    k = box([L + 10, 30, W + 10]); k.apply_translation([0, 15 if top else -15, 0]); return mesh.intersection(k, **M)
dome_part, base_part = half(shell, True), half(shell, False)

# ---------- clasp box: 35 x 8 x 14 ----------
cL, cH, cW = 35.0, 8.0, 14.0
cb = rounded_block(cL, cH, cW, 6.0, 2.0).difference(rounded_block(cL - 2, cH - 2, cW - 2, 5.0, 1.0), **M)
ch2 = box([cL + 4, 3.4, 6.4]); ch2.apply_translation([0, cH / 2, 0]); cb = cb.difference(ch2, **M)   # band channel on the skin side
for dx in (-2.5, 2.5):
    hole = cylinder(radius=1.0, height=4, sections=24); hole.apply_translation([dx, -cH / 2, 0]); cb = cb.difference(hole, **M)

def export(mesh, name, flip=False):
    m = mesh.copy()
    m.apply_transform(trimesh.transformations.rotation_matrix(-np.pi / 2, [1, 0, 0]))   # Y-up -> Z-up for slicers
    if flip: m.apply_transform(trimesh.transformations.rotation_matrix(np.pi, [1, 0, 0]))
    m.apply_translation([0, 0, -m.bounds[0][2]])
    m.export(name)
    print(name, "extents", np.round(m.extents, 2), "watertight", m.is_watertight, "· resin ~", round(m.volume / 1000 * 1.15, 2), "g")

export(base_part, "firefly_centerpiece_base.stl")
export(dome_part, "firefly_centerpiece_dome.stl", flip=True)
export(cb, "firefly_clasp_box.stl")
